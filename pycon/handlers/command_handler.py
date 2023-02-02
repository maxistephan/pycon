import logging

from dataclasses import dataclass
from discord import Message
from typing import Callable, Dict, List, Optional

from pycon.handlers.persistence_handler import PersistenceHandler


@dataclass
class CommandContext:
    prefix: str
    command: str
    args: List[str]
    message: Message


class CommandHandler:

    def __init__(self) -> None:
        self.__commands: Dict[str, Callable] = {
            "help": self.pycon_help_command,
        }

    async def handle_command(self, ctx: CommandContext) -> None:
        logging.debug(f"Handling command: {ctx.message.content}")
        command: Optional[Callable] = self.__commands.get(ctx.command)
        if not command:
            logging.debug(f"Command {ctx.command} not found.")
            await ctx.message.channel.send(
                f'No such command "{ctx.command}".\n'
                f'Try "{ctx.prefix}help" to get a list of available commands."'
            )
        else:
            logging.debug(f"Executing command {ctx.command} {ctx.args}")
            await command(ctx)

    async def handle_rcon(self, ctx: CommandContext) -> None:
        logging.debug(f"Handling RCON command {ctx.command} {ctx.args}")
        pass

    async def pycon_help_command(self, ctx: CommandContext) -> None:
        logging.debug(f"Executing help command")
        await ctx.message.channel.send(self._pycon_help_text())

    def _pycon_help_text(self) -> str:
        return PersistenceHandler.get_help_text_pycon()
