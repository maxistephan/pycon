import json
import logging
import os

from enum import Enum
from pathlib import Path
from typing import Dict, List

BASE_PATH = Path("/opt/pycon")
CHANNEL_AUTH_FILE = BASE_PATH / "auth_channels.json"
PREFIX_FILE = BASE_PATH / "prefixes.json"


class PersistenceMethod(Enum):
    JSON = "json"
    SQLITE = "sqlite"


class PersistenceHandler:
    @staticmethod
    def get_auth_channels(method: PersistenceMethod = PersistenceMethod.JSON) -> List[int]:
        logging.debug(f"Getting channels with method {method.name}")
        channels: List[int] = []
        if method == PersistenceMethod.JSON:
            if not CHANNEL_AUTH_FILE.exists():
                logging.info(f"Channel auth file not found, creating one at {CHANNEL_AUTH_FILE}")
                with open(CHANNEL_AUTH_FILE, "w") as auth_file:
                    auth_file.write(json.dumps(channels))
                return channels
            with open(CHANNEL_AUTH_FILE, "r") as auth_file:
                content = auth_file.read()
                channels = json.loads(content) if content else []
        elif method == PersistenceMethod.SQLITE:
            logging.warn("No SQLITE Implementation yet!")

        return channels

    @staticmethod
    def get_prefixes(method: PersistenceMethod = PersistenceMethod.JSON) -> Dict[int, str]:
        logging.debug(f"Getting prefixes with method {method.name}")
        prefixes: Dict[int, str] = {}
        if method == PersistenceMethod.JSON:
            if not PREFIX_FILE.exists():
                logging.info(f"Server prefix file not found, creating one at {PREFIX_FILE}")
                with open(PREFIX_FILE, "w") as prefix_file:
                    prefix_file.write(json.dumps(prefixes))
                return prefixes
            with open(PREFIX_FILE, "r") as prefix_file:
                content: str = prefix_file.read()
                prefixes = json.loads(content)
        elif method == PersistenceMethod.SQLITE:
            logging.warn("No SQLITE Implementation yet!")

        return prefixes

    @staticmethod
    def save_auth_channels(channels: List[int], method: PersistenceMethod = PersistenceMethod.JSON):
        if method == PersistenceMethod.JSON:
            logging.debug(f"Saving authorized channels to {CHANNEL_AUTH_FILE}")
            with open(CHANNEL_AUTH_FILE, "w") as auth_file:
                auth_file.write(json.dumps(channels))
        elif method == PersistenceMethod.SQLITE:
            logging.warn("No SQLITE Implementation yet!")

    @staticmethod
    def save_prefixes(prefix_dict: Dict[int, str], method: PersistenceMethod = PersistenceMethod.JSON):
        if method == PersistenceMethod.JSON:
            logging.debug(f"Saving prefixes to {PREFIX_FILE}")
            with open(PREFIX_FILE, "w") as prefix_file:
                prefix_file.write(json.dumps(prefix_dict))
        elif method == PersistenceMethod.SQLITE:
            logging.warn("No SQLITE Implementation yet!")