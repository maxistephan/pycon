#!/usr/bin/python3

"""Daemon for the pycon Discord Bot

Description:    Daemon for the pycon Discord Bot
Author:         Maximilian Stephan
Disclaimer:     Copyright (c) 2023 Maximilian Stephan,
                ALL RIGHTS RESERVED - Unauthorized copying of this file,
                via any medium is strictly prohibited.
"""

import logging
import signal
from typing import List

from pycon.client.argument_parser import parse_args
from pycon.client.client import PyconClient


def setup_logging(loglevel: str):
    """Setup the Application Logging

    Args:
        loglevel (str): Loglevel String in all-caps
    """
    # Setup Logging
    logging.basicConfig(level=logging.getLevelName(loglevel))
    logging.info("Logging setup completed")


def setup_signal_handlers(pycon_client: PyconClient):
    """Setup what happens on SIGINT and SIGTERM

    Args:
        pycon_client (PyconClient): Client of the PYCON Bot
    """
    logging.info("Setting up signal handlers")
    signal.signal(signal.SIGINT, pycon_client.handle_signal)
    signal.signal(signal.SIGTERM, pycon_client.handle_signal)


def setup_client(token: str, servers: List[str]):
    """Setup the Pycon Client

    Args:
        token (str): Token of the Bot. Get this from https://discord.com/developers
        servers (List[str]): List of guilds
    """
    logging.info("Setting up Pycon Client")
    pycon_client: PyconClient = PyconClient(token=token, servers=servers)
    setup_signal_handlers(pycon_client)
    pycon_client.start_client()


def main():
    """Pycon main method"""
    args = parse_args()
    setup_logging(args.loglevel)
    setup_client(args.token, args.servers)


if __name__ == "__main__":
    main()
