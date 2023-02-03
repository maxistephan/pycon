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
import sys
from typing import Any, Callable, Dict, List

import discord

from pycon.handlers.command_handler import CommandContext, CommandHandler
from pycon.handlers.persistence_handler import PersistenceHandler

DEFAULT_PREFIX = "$"


class PyconClient(discord.Client):
    """Pycon Bot Client Class

    Args:
        token (str): Token for the Discord Bot
        servers (List[str]): List of guilds
    """
    def __init__(self, token: str, servers: List[str] = None) -> None:
        intents: discord.Intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.__token = token
        self.__servers = servers if servers else []
        self.__authorized_channels: List[int] = PersistenceHandler.get_auth_channels()
        self.__prefixes: Dict[int, str] = PersistenceHandler.get_prefixes()
        self.__command_handler = CommandHandler()
        self.__command_handler.add_command(
            "set-prefix", self._prefix_setter, "Change the command prefix"
        )

        @self.event
        async def on_ready():
            logging.info("Logged in as %s with servers %s", self.user, self.__servers)

        @self.event
        async def on_message(message: discord.Message):
            if message.author == self.user:
                return

            prefix = self.get_prefix_for_server(message.channel.guild)
            message.content = message.content.strip()
            handler: Callable = None

            if message.content.startswith(prefix):
                message.content = message.content[len(prefix):]
                handler = self.__command_handler.handle_command
            elif message.channel.id in self.__authorized_channels:
                handler = self.__command_handler.handle_rcon

            if handler:
                content_list: List[str] = message.content.split(" ")
                command: str = content_list[0] if content_list else ""
                args: List[str] = content_list[1:] if len(content_list) > 1 else []
                ctx: CommandContext = CommandContext(prefix, command, args, message)
                try:
                    await handler(ctx)
                except Exception:
                    ctx.message.channel.send("I'm sorry, something bad happend on my end :(")
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

    async def _prefix_setter(self, ctx: CommandContext) -> None:
        if ctx.args:
            self.set_prefix_for_server(ctx.message.guild, ctx.args[0])
            await ctx.message.channel.send(f'Your prefix has been changed to "{ctx.args[0]}"')
        else:
            await ctx.message.channel.send("Please enter a prefix!")
