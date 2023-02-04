"""Command handling module for pycon

Description:    Command handling module for pycon
Author:         Maximilian Stephan
Disclaimer:     Copyright (c) 2023 Maximilian Stephan,
                ALL RIGHTS RESERVED - Unauthorized copying of this file,
                via any medium is strictly prohibited.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple, Union

from discord import Color, Embed, Message


class CommandAuthStage(Enum):
    """Authorization Level for a command to be executed."""
    CROOK = 1
    HITMAN = 2
    BOSS = 3


@dataclass
class BotCommand:
    """Dataclass representation of a command for the bot"""
    name: str
    handler: Callable
    help_text: str
    auth_stage: CommandAuthStage


@dataclass
class CommandContext:
    """Context of a Bot Command"""
    prefix: str
    command: str
    args: List[str]
    message: Message


class CommandHandler:
    """Handling for bot and rcon commands in text channels."""
    def __init__(self) -> None:
        self.__commands: Dict[str, BotCommand] = {
            "help": BotCommand(
                "help",
                self.pycon_help_command,
                "Print this helping text",
                CommandAuthStage.CROOK
            ),
        }

    def add_commands(
        self,
        commands: List[Union[Tuple[str, Callable, str, CommandAuthStage], BotCommand]]
    ) -> None:
        """Add a command that is being picked up in channels

        Args:
            commands (List[Union[Tuple[str, Callable, str, CommandAuthStage], BotCommand]]):
                Commands to be added
        """
        for command in commands:
            if isinstance(command, BotCommand):
                self.add_command(command)
            else:
                self.add_command(BotCommand(command[0], command[1], command[2], command[3]))

    def add_command(
        self,
        bot_command: BotCommand,
    ) -> None:
        """Add a command that is being picked up in channels

        Args:
            name (str): name of the command (e.g. "$help" -> name := help)
            handler (Callable): handler for the command. Function will be called with arg:
                                ctx: CommandContext
            help_text (str): Helpful text that is being displayed when using the "$help" command
        """
        self.__commands[bot_command.name] = bot_command

    async def handle_command(self, ctx: CommandContext) -> None:
        """Handle the command in a text channel.
        Gets called when users use the prefix at the start of their message.

        Args:
            ctx (CommandContext): Context in which the command is used
        """
        logging.debug("Handling command: %s", ctx.message.content)
        command: Optional[BotCommand] = self.__commands.get(ctx.command)
        if not command:
            logging.debug("Command %s not found.", ctx.command)
            await ctx.message.channel.send(
                f'No such command "{ctx.command}".\n'
                f'Try "{ctx.prefix}help" to get a list of available commands."'
            )
        else:
            logging.debug("Executing command %s %s", ctx.command, ctx.args)
            await command.handler(ctx)

    async def pycon_help_command(self, ctx: CommandContext) -> None:
        """Display Help Text

        Args:
            ctx (CommandContext): Context in which the command is used
        """
        await ctx.message.channel.send(embed=self._pycon_help(ctx.prefix))

    def _pycon_help(self, prefix: str) -> Embed:
        """Generate an Embed for help texts

        Args:
            prefix (str): Prefix of the Server

        Returns:
            Embed: Embed with helpful information about pycon usage
        """
        embed: Embed = Embed(
            title="Usage",
            url="https://realdrewdata.medium.com/",
            description="Welcome! If you haven't already, try authorizing a channel for RCON!",
            color=Color.green()
        )
        for command in self.__commands.values():
            embed.add_field(
                name=f"{prefix}{command.name}",
                value=f"{command.help_text} (Auth Stage: {command.auth_stage.value})", inline=False
            )

        return embed
