import logging

from dataclasses import dataclass
from discord import Embed, Message, Color
from typing import Callable, Dict, List, Optional

from pycon.handlers.persistence_handler import PersistenceHandler


@dataclass
class BotCommand:
    name: str
    handler: Callable
    help_text: str


@dataclass
class CommandContext:
    prefix: str
    command: str
    args: List[str]
    message: Message


class CommandHandler:
    def __init__(self) -> None:
        self.__commands: Dict[str, BotCommand] = {
            "help": BotCommand("help", self.pycon_help_command, "Print this helping text"),
        }

    def add_command(self, name: str, handler: Callable, help_text: str) -> None:
        self.__commands[name] = BotCommand(name, handler, help_text)

    async def handle_command(self, ctx: CommandContext) -> None:
        logging.debug(f"Handling command: {ctx.message.content}")
        command: Optional[BotCommand] = self.__commands.get(ctx.command)
        if not command:
            logging.debug(f"Command {ctx.command} not found.")
            await ctx.message.channel.send(
                f'No such command "{ctx.command}".\n'
                f'Try "{ctx.prefix}help" to get a list of available commands."'
            )
        else:
            logging.debug(f"Executing command {ctx.command} {ctx.args}")
            await command.handler(ctx)

    async def handle_rcon(self, ctx: CommandContext) -> None:
        logging.debug(f"Handling RCON command {ctx.command} {ctx.args}")
        logging.error(f"RCON Not implemented yet")

    async def pycon_help_command(self, ctx: CommandContext) -> None:
        await ctx.message.channel.send(embed=self._pycon_help(ctx.prefix))

    async def rcon_help_command(self, ctx: CommandContext) -> None:
        logging.debug(f"Executing help command")
        await ctx.message.channel.send(embed=self._rcon_help())

    def _rcon_help(self) -> Embed:
        logging.error(f"RCON Not implemented yet")
        return Embed()

    def _pycon_help(self, prefix: str) -> Embed:
        embed: Embed = Embed(
            title="Usage",
            url="https://realdrewdata.medium.com/",
            description="Welcome! If you haven't already, try authorizing a channel for RCON!",
            color=Color.green()
        )
        for command in self.__commands.values():
            embed.add_field(name=f"{prefix}{command.name}", value=command.help_text, inline=False)

        return embed
