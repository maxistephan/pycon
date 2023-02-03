"""CLI argument parser for pycon

Description:    CLI argument parser for pycon
Author:         Maximilian Stephan
Disclaimer:     Copyright (c) 2023 Maximilian Stephan,
                ALL RIGHTS RESERVED - Unauthorized copying of this file,
                via any medium is strictly prohibited.
"""

import os
from argparse import ArgumentParser, Namespace
from typing import List

TOKEN_VAR = "PYCON_BOT_TOKEN"
SERVERS_VAR = "PYCON_DISCORD_SERVERS"


def parse_args() -> Namespace:
    """Get the argparse Namespace with defined arguments from the commandline

    Raises:
        ValueError: If a wrong Argument is passed

    Returns:
        Namespace: argparse.Namespace with defined arguments from the commandline
    """
    parser: ArgumentParser = ArgumentParser()

    parser.add_argument("--token", "-t", type=str, default=None)
    parser.add_argument("--servers", type=List[str], default=None)
    parser.add_argument("--loglevel", type=str, default="INFO")

    args = parser.parse_args()

    if not args.token:
        token: str = os.getenv(TOKEN_VAR)
        if not token:
            raise ValueError(f"No Bot token passed. Either use cli or env var '{TOKEN_VAR}'")
        args.token: str = token

    if not args.servers:
        args.servers: List[str] = os.getenv(SERVERS_VAR, "").strip().split(" ")

    args.loglevel: str = args.loglevel.upper()

    return args
