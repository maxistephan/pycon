#!/usr/bin/python3

import argparse
import logging
import os
import signal

from datetime import datetime
from pathlib import Path
from typing import Any, List

from pycon.client.argument_parser import parse_args
from pycon.client.client import PyconClient


def setup_logging(loglevel: str):
    # Setup Logging
    logging.basicConfig(level=logging.getLevelName(loglevel))
    logging.info("Logging setup completed")


def setup_signal_handlers(pycon_client: PyconClient):
    logging.info("Setting up signal handlers")
    signal.signal(signal.SIGINT, pycon_client.handle_signal)
    signal.signal(signal.SIGTERM, pycon_client.handle_signal)


def setup_client(token: str, servers: List[str]):
    logging.info("Setting up Pycon Client")
    pycon_client: PyconClient = PyconClient(token=token, servers=servers)
    setup_signal_handlers(pycon_client)
    pycon_client.start_client()


def main():
    args = parse_args()
    setup_logging(args.loglevel)
    setup_client(args.token, args.servers)


if __name__ == "__main__":
    main()
