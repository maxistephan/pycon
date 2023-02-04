"""Authentication helper functions

Description:    Authentication helper functions for pycon
Author:         Maximilian Stephan
Disclaimer:     Copyright (c) 2023 Maximilian Stephan,
                ALL RIGHTS RESERVED - Unauthorized copying of this file,
                via any medium is strictly prohibited.
"""

import logging
import socket
from enum import Enum, auto
from typing import Any, Dict

from discord import TextChannel
from rcon.source import Client as RCONClient

from pycon.handlers.command_handler import CommandContext


class AuthStage(Enum):
    """Enum Class to represent Stages in Channel Authentication"""
    INIT = auto()
    COLLECT = auto()
    CHECK = auto()


class AuthException(Exception):
    """Custom Exception for Channel Authentication Errors"""


class ChannelAuthHandler:
    """Helper class for channel authentication

    Args:
        open_auths (Dict[int, Dict[str, Any]]): Pycon client's open authentications and their stage
        authorized_channels (Dict[str, Any]): Pycon client's authorized channels
    """

    def __init__(
        self, open_auths: Dict[int, Dict[str, Any]], authorized_channels: Dict[str, Any]
    ) -> None:
        self._open_auths: Dict[str, int] = open_auths
        self._authorized_channels: Dict[str, Any] = authorized_channels
        self._original_channel: TextChannel = None

    async def handle_auth(self, ctx: CommandContext):
        """Handle channel authentication

        Args:
            ctx (CommandContext): Command Context
        """
        channel_config = self._open_auths.get(ctx.message.author.id)
        if not channel_config:
            channel_config = self._basic_auth_config(ctx.message.channel)
        logging.debug("Channel Config: %s", channel_config)
        channel_stage: AuthStage = channel_config["stage"]
        if channel_stage == AuthStage.INIT:
            self._open_auths[ctx.message.author.id] = channel_config
            await self.start_auth(ctx)
        elif channel_stage == AuthStage.COLLECT:
            await self.collect_creds(ctx)
        elif channel_stage == AuthStage.CHECK:
            await self.check_creds(ctx)
        else:
            raise AuthException("Unknown Authentication Stage!")

    async def start_auth(self, ctx: CommandContext):
        """Start channel authentication

        Args:
            ctx (CommandContext): Command Context
        """
        author: str = ctx.message.author.mention
        await ctx.message.channel.send(
            f"I slid into your DMs {author}. Fill out the credentials there!"
        )
        prompt = (
            "Enter RCON Credentials in the following Format:\n"
            "```\n"
            "HOST:PORT PASSWORD [TYPE]\n"
            "```\n"
            "Where HOST is you RCON IP address, PORT is the RCON port, PASSWORD is your password "
            "and TYPE is the type of server you have (e.g. Minecraft, ARK, ...).\n"
            "TYPE is optional and defaults to 'Minecraft'.\n"
            'Write "abort" to end configuration.'
        )
        await ctx.message.author.send(prompt)
        self._open_auths[ctx.message.author.id]["stage"] = AuthStage.COLLECT


    async def collect_creds(self, ctx: CommandContext):
        """Collect channel credentials from command context's message

        Args:
            ctx (CommandContext): Command Context
        """
        if ctx.command.lower() == "abort" and not ctx.args:
            await ctx.message.channel.send("As you wish. Authentication is aborted.")
            await self._open_auths[ctx.message.author.id]["orig_channel"].send(
                f"Connection aborted. {ctx.message.author.mention} f*cked up the authentication."
            )
            del self._open_auths[ctx.message.author.id]
            return

        host_port = ctx.command.split(":")
        host = host_port[0]
        port = 25575
        password = ""
        rcon_type = "Minecraft"
        try:
            port = int(host_port[1])
        except IndexError as err:
            logging.error("No port submitted: %s", err)
            await ctx.message.channel.send("You forgot the port. Use it like this: HOST:PORT")
            return
        except ValueError as err:
            logging.error("Port is not a number: %s", err)
            await ctx.message.channel.send("The port has to be a number!")
            return
        try:
            password = ctx.args[0]
        except IndexError as err:
            logging.error("No password submitted: %s", err)
            await ctx.message.channel.send("Sorry, that is the wrong format. Try again!")
            return
        rcon_type = ctx.args[1] if len(ctx.args) > 1 else rcon_type
        # Remove Brackets if there are idiots
        if rcon_type.startswith("["):
            rcon_type = rcon_type[1:]
        if rcon_type.endswith("]"):
            rcon_type = rcon_type[:-1]

        self._authorized_channels[
            f"{self._open_auths[ctx.message.author.id]['orig_channel'].id}"
        ] = {
            "authorized": False,
            "rcon": host,
            "port": port,
            "password": password,
            "type": rcon_type,
        }
        await ctx.message.channel.send(
            "Wonderful. Would you like to check your login credentials for validity? (y/n)"
        )
        self._open_auths[ctx.message.author.id]["stage"] = AuthStage.CHECK

    async def check_creds(self, ctx: CommandContext):
        """Collect channel credentials from command context's message

        Args:
            ctx (CommandContext): Command Context
        """
        if ctx.command == "y":
            creds = self._authorized_channels[
                f"{self._open_auths[ctx.message.author.id]['orig_channel'].id}"
            ]
            try:
                with RCONClient(creds["rcon"], creds["port"], passwd=creds["password"]):
                    pass
            except (ConnectionRefusedError, socket.gaierror) as err:
                logging.error("Couldn't connect to rcon: %s", err)
                await ctx.message.channel.send(
                    "Connection not possible. Try again."
                )
                self._open_auths[ctx.message.author.id]["stage"] = AuthStage.COLLECT
                return
        elif ctx.command == "n":
            await ctx.message.channel.send("Alright, your call man")
        else:
            await ctx.message.channel.send(
                "That ain't valid. Try again: 'y' for yes and 'n' for no."
            )
            return

        await self._open_auths[ctx.message.author.id]["orig_channel"].send("Connected!")
        self._authorized_channels[f"{self._open_auths[ctx.message.author.id]['orig_channel'].id}"] \
            ["authorized"] = True
        del self._open_auths[ctx.message.author.id]

    def _basic_auth_config(self, channel: TextChannel) -> Dict[str, Any]:
        """Get a basic auth config dictionary

        Args:
            channel (MessageableChannel): Channel to be authorized

        Returns:
            Dict[str, Any]: Basic auth config dictionary in following format:
                {
                    "orig_channel": MessageableChannel,
                    "stage": AuthStage,
                }
        """
        return {
            "orig_channel": channel,
            "stage": AuthStage.INIT,
        }
