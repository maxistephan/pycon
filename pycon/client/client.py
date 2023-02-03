from __future__ import annotations

import discord
import logging
import os
import signal
import sys
import json

from typing import Any, Callable

from pycon.handlers.persistence_handler import PersistenceHandler
from pycon.handlers.command_handler import CommandContext, CommandHandler

DEFAULT_PREFIX = "$"


class PyconClient(discord.Client):
    def __init__(self, token: str, servers: List[str] = None) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
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
            print(f'We have logged in as {self.user}')

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
                await handler(ctx)

    def start_client(self) -> None:
        self.run(self.__token)

    def get_prefix_for_server(self, server: discord.client.Guild) -> str:
        id = server.id if server else None
        if id:
            return self.__prefixes.get(id) or DEFAULT_PREFIX
        else:
            logging.debug("No Server passed. Skipping prefix collection.")
            return DEFAULT_PREFIX

    def set_prefix_for_server(self, server: discord.client.Guild, prefix: str) -> None:
        id = server.id if server else None
        if id:
            self.__prefixes[id] = prefix
        else:
            logging.warn("No Server passed. Skipping prefix assignment.")

    def _cleanup(self) -> None:
        PersistenceHandler.save_auth_channels(self.__authorized_channels)
        PersistenceHandler.save_prefixes(self.__prefixes)

    def handle_signal(self, signum: int, frame: Any) -> None:
        logging.info(f"Stopping Pycon Bot after signal {signum}: {signal.Signals(signum).name}")
        self._cleanup()
        self.clear()
        sys.exit(0)

    async def _prefix_setter(self, ctx: CommandContext) -> None:
        if ctx.args:
            self.set_prefix_for_server(ctx.message.guild, ctx.args[0])
            await ctx.message.channel.send(f'Your prefix has been changed to "{ctx.args[0]}"')
        else:
            await ctx.message.channel.send("Please enter a prefix!")
