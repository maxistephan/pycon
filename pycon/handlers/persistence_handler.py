"""Persistence helper functions

Description:    Persistence helper functions for pycon
Author:         Maximilian Stephan
Disclaimer:     Copyright (c) 2023 Maximilian Stephan,
                ALL RIGHTS RESERVED - Unauthorized copying of this file,
                via any medium is strictly prohibited.
"""

import json
import logging
import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

BASE_PATH = Path.home() / ".local/share/pycon"
CHANNEL_AUTH_FILE = BASE_PATH / "auth_channels.json"
PREFIX_FILE = BASE_PATH / "prefixes.json"
SYS_AUTH_FILE = BASE_PATH / "authorized_users.json"


class PersistenceMethod(Enum):
    """Method which persists data

    Args:
        Enum (str): Enum values represent file suffixes
    """
    JSON = "json"
    SQLITE = "sqlite"


class PersistenceHandler:
    """Persistence facade to save information"""
    @staticmethod
    def get_auth_channels(method: PersistenceMethod = PersistenceMethod.JSON) -> Dict[str, Any]:
        """Return all authorized channel-ids, mapped to their properties as a Dictionary

        Args:
            method (PersistenceMethod, optional): Method that is preferred to get persistence from.
                Defaults to PersistenceMethod.JSON.

        Returns:
            Dict[str, Any]: All authorized channel-ids, mapped to their properties as a Dictionary
        """
        logging.debug("Getting channels with method %s", method.name)
        channels: Dict[str, Any] = {}
        if not BASE_PATH.exists():
            os.makedirs(BASE_PATH)
        if method == PersistenceMethod.JSON:
            if not CHANNEL_AUTH_FILE.exists():
                logging.info("Channel auth file not found, creating one at %s", CHANNEL_AUTH_FILE)
                with open(CHANNEL_AUTH_FILE, "w", encoding="utf-8") as auth_file:
                    auth_file.write(json.dumps(channels))
                return channels
            with open(CHANNEL_AUTH_FILE, "r", encoding="utf-8") as auth_file:
                content = auth_file.read()
                channels = json.loads(content) if content else {}
        elif method == PersistenceMethod.SQLITE:
            logging.warning("No SQLITE Implementation yet!")

        return channels

    @staticmethod
    def get_prefixes(method: PersistenceMethod = PersistenceMethod.JSON) -> Dict[int, str]:
        """Get all Servers/Guilds and their prefixes as a Dictionary

        Args:
            method (PersistenceMethod, optional): Method that is preferred to get persistence from.
                Defaults to PersistenceMethod.JSON.

        Returns:
            Dict[int, str]: All Servers/Guilds and their prefixes as a Dictionary
        """
        logging.debug("Getting prefixes with method %s", method.name)
        prefixes: Dict[int, str] = {}
        if method == PersistenceMethod.JSON:
            if not PREFIX_FILE.exists():
                logging.info("Server prefix file not found, creating one at %s", PREFIX_FILE)
                with open(PREFIX_FILE, "w", encoding="utf-8") as prefix_file:
                    prefix_file.write(json.dumps(prefixes))
                return prefixes
            with open(PREFIX_FILE, "r", encoding="utf-8") as prefix_file:
                content: str = prefix_file.read()
                prefixes = json.loads(content)
        elif method == PersistenceMethod.SQLITE:
            logging.warning("No SQLITE Implementation yet!")

        return prefixes

    @staticmethod
    def save_auth_channels(
        channels: Dict[str, Any], method: PersistenceMethod = PersistenceMethod.JSON
    ):
        """Persist all authorized channels

        Args:
            channels (Dict[int, Any]): Dict of channel-ids as keys and important data as values
            method (PersistenceMethod, optional): Method that is preferred to persist data.
                Defaults to PersistenceMethod.JSON.
        """
        if method == PersistenceMethod.JSON:
            logging.debug("Saving authorized channels to  %s", CHANNEL_AUTH_FILE)
            with open(CHANNEL_AUTH_FILE, "w", encoding="utf-8") as auth_file:
                auth_file.write(json.dumps(channels))
        elif method == PersistenceMethod.SQLITE:
            logging.warning("No SQLITE Implementation yet!")

    @staticmethod
    def save_prefixes(
        prefix_dict: Dict[int, str], method: PersistenceMethod = PersistenceMethod.JSON
    ):
        """Persist all Prefixes for each Server/Guild

        Args:
            prefix_dict (Dict[int, str]): Dictionary object containing Server/Guild IDs as Key and
                their prefix as value.
            method (PersistenceMethod, optional): Method that is preferred to persist data.
                Defaults to PersistenceMethod.JSON.
        """
        if method == PersistenceMethod.JSON:
            logging.debug("Saving prefixes to %s", PREFIX_FILE)
            with open(PREFIX_FILE, "w", encoding="utf-8") as prefix_file:
                prefix_file.write(json.dumps(prefix_dict))
        elif method == PersistenceMethod.SQLITE:
            logging.warning("No SQLITE Implementation yet!")

    @staticmethod
    def get_authorized_users(method: PersistenceMethod = PersistenceMethod.JSON) -> List[int]:
        """Get a list of BOSS users

        Args:
            method (PersistenceMethod, optional): Method of persistence.
                Defaults to PersistenceMethod.JSON.

        Returns:
            List[int]: List of all users with auth level "BOSS"
        """
        auths: List[int] = []
        if method == PersistenceMethod.JSON:
            if not SYS_AUTH_FILE.exists():
                logging.info("Sys auth file not found, creating one at %s", SYS_AUTH_FILE)
                with open(SYS_AUTH_FILE, "w", encoding="utf-8") as sys_auth:
                    sys_auth.write(json.dumps(auths))
                return auths
            with open(SYS_AUTH_FILE, "r", encoding="utf-8") as sys_auth:
                content: str = sys_auth.read()
                auths = json.loads(content)
        elif method == PersistenceMethod.SQLITE:
            logging.warning("No SQLITE Implementation yet!")
        return auths
