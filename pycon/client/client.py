"""Pycon client module

Description:    Pycon client module
Author:         Maximilian Stephan
Disclaimer:     Copyright (c) 2023 Maximilian Stephan,
                ALL RIGHTS RESERVED - Unauthorized copying of this file,
                via any medium is strictly prohibited.
"""

from __future__ import annotations

import logging
import signal
import socket
import sys
from typing import Any, Callable, Dict, List

import discord
from rcon.source import Client as RCONClient

from pycon.handlers.auth_handler import ChannelAuthHandler
from pycon.handlers.command_handler import CommandAuthStage, CommandContext, CommandHandler
from pycon.handlers.persistence_handler import PersistenceHandler
from pycon.handlers.system_handler import SystemHandler

DEFAULT_PREFIX = "r!"


class PyconClient(discord.Client):
    """Pycon Bot Client Class

    Args:
        token (str): Token for the Discord Bot
        servers (List[str]): List of guilds
    """
    def __init__(self, token: str, servers: List[str] = None) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.__token = token
        self.__servers = servers if servers else []
        self.__authorized_channels: Dict[str, Any] = PersistenceHandler.get_auth_channels()
        self.__open_auths: Dict[int, Dict[Any]] = {}
        self.__prefixes: Dict[int, str] = PersistenceHandler.get_prefixes()
        self.__command_handler = CommandHandler()
        self.__command_handler.add_commands([
            (
                "set-prefix",
                self._prefix_setter,
                "Change the command prefix",
                CommandAuthStage.HITMAN
            ),
            (
                "authorize",
                self.authorize_channel_command,
                "Authorize a channel to send rcon messages",
                CommandAuthStage.HITMAN
            ),
            (
                "deauthorize",
                self.deauthorize_channel_command,
                "Deauthorize a channel from sending rcon messages",
                CommandAuthStage.HITMAN
            ),
            (
                "restart",
                SystemHandler(self.__authorized_channels).handle_sys_command,
                "Restart the authorized server of this channel",
                CommandAuthStage.BOSS
            ),
        ])

    async def on_ready(self):
        """Gets Called when the Bot is ready"""
        logging.info("Logged in as %s with servers %s", self.user, self.__servers)
        client_id = 930480521186803782
        invite_link = (
            "https://discordapp.com/oauth2/authorize?"
            f"client_id={client_id}&scope=bot"
        )
        logging.info("Use %s to invite the bot to your server!", invite_link)
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name=f"with yo mamas ballz lol | {DEFAULT_PREFIX}help"
            )
        )


    async def on_message(self, message: discord.Message):
        """Gets Called on message"""
        if message.author == self.user:
            return
        logging.debug(
            "Got message from %s (%d): %s",
            message.author,
            message.author.id,
            message.content
        )
        prefix = self.get_prefix_for_server(message.channel.guild)
        message.content = message.content.strip()
        handler: Callable = None
        auth_channel: Dict[str, Any] = self.__authorized_channels.get(f"{message.channel.id}")

        if message.content.startswith(prefix):
            message.content = message.content[len(prefix):]
            handler = self.__command_handler.handle_command
        elif auth_channel:
            if auth_channel["authorized"]:
                # Set this prefix for rcon commands
                # prefix = auth_channel["prefix"]
                handler = self.handle_rcon
        elif not isinstance(message.channel, discord.channel.DMChannel) and not auth_channel:
            # Create entry in channels if not already done
            self.__authorized_channels[f"{message.channel.id}"] = self._basic_channel_auth()
        elif self.__open_auths.get(message.author.id):
            handler = ChannelAuthHandler(
                self.__open_auths, self.__authorized_channels
            ).handle_auth

        if not handler is None:
            content_list: List[str] = message.content.split(" ")
            command: str = content_list[0] if content_list else ""
            args: List[str] = content_list[1:] if len(content_list) > 1 else []
            ctx: CommandContext = CommandContext(prefix, command, args, message)
            try:
                await handler(ctx)
            except Exception:
                await ctx.message.channel.send("I'm sorry, something bad happend on my end :(")
                raise

    def start_client(self) -> None:
        """Start the Bot and all listeners"""
        self.run(self.__token)

    def get_prefix_for_server(self, server: discord.client.Guild) -> str:
        """Get the prefix for a server

        Args:
            server (discord.client.Guild): Server for which the prefix is required

        Returns:
            str: Server specific prefix, if it has been altered, else the default prefix
        """
        s_id = server.id if server else None
        if s_id:
            return self.__prefixes.get(s_id) or DEFAULT_PREFIX
        else:
            logging.debug("No Server passed. Skipping prefix collection.")
            return DEFAULT_PREFIX

    async def authorize_channel_command(self, ctx: CommandContext):
        """Authorize a channel.

        Args:
            ctx (CommandContext): Command Context
        """
        if isinstance(ctx.message.channel, discord.channel.DMChannel):
            await ctx.message.channel.send("You cannot authorize a private channel!")
            return
        self.__open_auths[ctx.message.author.id] = None
        await ChannelAuthHandler(self.__open_auths, self.__authorized_channels).handle_auth(ctx)
        logging.debug("Started authorizing: %s", self.__open_auths)

    async def deauthorize_channel_command(self, ctx: CommandContext):
        """Deauthorize a channel.

        Args:
            ctx (CommandContext): Command Context
        """
        if not ctx.message.guild:
            await ctx.message.channel.send("You cannot deauthorize a private channel!")
            return
        channel_cfg = self.__authorized_channels.get(f"{ctx.message.channel.id}")
        if channel_cfg:
            channel_cfg["authorized"] = False
            ctx.message.channel.send("Your channel has been deauthorized.")
        else:
            await ctx.message.channel.send("This Channel is not yet authorized.")

    def set_prefix_for_server(self, server: discord.client.Guild, prefix: str) -> None:
        """Change the Prefix of a server

        Args:
            server (discord.client.Guild): Server for which the prefix is being changed
            prefix (str): New Prefix for the server
        """
        s_id = server.id if server else None
        if s_id:
            self.__prefixes[s_id] = prefix
        else:
            logging.warning("No Server passed. Skipping prefix assignment.")

    def _cleanup(self) -> None:
        """Clean up the Bot and save all properties that need persistence."""
        PersistenceHandler.save_auth_channels(self.__authorized_channels)
        PersistenceHandler.save_prefixes(self.__prefixes)

    def handle_signal(self, signum: int, frame: Any) -> None:
        """Handle SIGINT and SIGTERM signals and exit gracefully

        Args:
            signum (int): Number of the signal (e.g. 2 := SIGINT)
            frame (Any): current stack frame (None or a frame object)
        """
        logging.info(
            "Stopping Pycon Bot after signal %d: %s in frame %s",
            signum,
            signal.Signals(signum).name,
            frame
        )
        self._cleanup()
        self.clear()
        sys.exit(0)

    async def handle_rcon(self, ctx: CommandContext) -> None:
        """Handle RCON commands.
        Forwards messages to rcon, if message is received in an authorized channel, regardless the
        prefix.

        Args:
            ctx (CommandContext): Context in which the command is used
        """
        logging.debug("Handling RCON command %s %s", ctx.command, ctx.args)
        creds = self.__authorized_channels[f"{ctx.message.channel.id}"]
        if creds["type"] == "Minecraft":
            ctx.prefix = "/"
        if (ctx.command.lower == "stop" and
            not ctx.message.author.id in SystemHandler.get_authorized_users()):
            await ctx.message.channel.send("Nah bro u aint stopping that shit now dawg")
            return
        try:
            with RCONClient(creds["rcon"], creds["port"], passwd=creds["password"]) as rcon_client:
                response = rcon_client.run(f"{ctx.prefix}{ctx.command}", *ctx.args)
                if response:
                    await ctx.message.channel.send(response)
        except (ConnectionRefusedError, socket.gaierror) as err:
            logging.error("Got connection refused when connecting to rcon: %s", err)
            await ctx.message.channel.send("Connection Failed. Try authorizing this channel again.")
        except discord.errors.HTTPException as err:
            logging.error("Got HTTP Error: %s", err)
            await ctx.message.channel.send(
                "The requested Message is too long for Discord. Must be 2000 or fewer in length!"
            )

    def _basic_channel_auth(self) -> Dict[str, Any]:
        return {
            "authorized": False,
            "rcon": "",
            "port": "",
            "password": "",
            "type": "",
        }

    async def _prefix_setter(self, ctx: CommandContext) -> None:
        if ctx.args:
            self.set_prefix_for_server(ctx.message.guild, ctx.args[0])
            await ctx.message.channel.send(f'Your prefix has been changed to "{ctx.args[0]}"')
        else:
            await ctx.message.channel.send("Please enter a prefix!")
