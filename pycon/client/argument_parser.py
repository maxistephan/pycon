import os

from argparse import ArgumentParser, Namespace
from typing import List


TOKEN_VAR = "PYCON_BOT_TOKEN"
SERVERS_VAR = "PYCON_DISCORD_SERVERS"


def parse_args() -> Namespace:
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
        args.servers: List[str] = os.getenv(SERVERS_VAR, [])

    args.loglevel: str = args.loglevel.upper()

    return args
