"""System handler

Description:    System handler for system commands in pycon
Author:         Maximilian Stephan
Disclaimer:     Copyright (c) 2023 Maximilian Stephan,
                ALL RIGHTS RESERVED - Unauthorized copying of this file,
                via any medium is strictly prohibited.
"""

import logging
import subprocess
from typing import Any, Dict, List

from pycon.handlers.command_handler import CommandContext
from pycon.handlers.persistence_handler import PersistenceHandler


class SystemHandler:
    """Class representation for System Command Handling
    """
    def __init__(self, auth_channels: Dict[str, Any]) -> None:
        self._auth_channels = auth_channels

    async def handle_sys_command(self, ctx: CommandContext):
        """Handle System command

        Args:
            ctx (CommandContext): Command Context
        """
        logging.warning(
            "User %s (%d) tried to execute a system command: %s %s",
            ctx.message.author,
            ctx.message.author.id,
            ctx.command,
            ctx.args,
        )
        auth_users: List[int] = SystemHandler.get_authorized_users()
        logging.warning("Authorized users: %s", auth_users)
        if not ctx.message.author.id in auth_users:
            await ctx.message.channel.send("You don't have permissions for this command.")
            return
        if ctx.command == "restart":
            await self.command_restart(ctx)


    async def command_restart(self, ctx: CommandContext):
        """Restart the desired server

        Args:
            ctx (CommandContext): Command Context
        """
        server_config = self._auth_channels.get(f"{ctx.message.channel.id}")
        if not server_config:
            await ctx.message.channel.send("This channel isn't authorized yet.")
            return
        server_type: str = server_config["type"].strip().lower()
        try:
            await ctx.message.channel.send("Trying to restart server ...")
            process_out = subprocess.check_output(
                f"systemctl restart {server_type}",
                shell=True,
            )
            logging.debug("Process finished: %s", process_out)
        except subprocess.CalledProcessError as err:
            await ctx.message.channel.send("That didnt work, sorry pal")
            logging.error("Error in sys comman: %s", err)
            return
        await ctx.message.channel.send("Server is restarting. This could take a minute.")

    @staticmethod
    def get_authorized_users() -> List[int]:
        """Get all authorized users as a List of strings

        Returns:
            List[int]: Authoried Usernames
        """
        return PersistenceHandler.get_authorized_users()
