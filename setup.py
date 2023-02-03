#!/usr/bin env python3

"""Module setup for pycon"""

import subprocess
import sys
from pathlib import Path
from typing import List

from setuptools import find_packages, setup

_VERSION: str = "0.0.0-dirty"
REQ_FILE: Path = Path("requirements.txt")


def get_requirements() -> List[str]:
    """Collect the requirements for this module"""
    if not REQ_FILE.exists():
        try:
            subprocess.check_output("pip-compile")
        except subprocess.CalledProcessError:
            print("pip-tools package is not installed. Use 'python3 -m pip install pip-tools'")
            sys.exit(1)

    with open(REQ_FILE, "r", encoding="utf-8") as pipfile:
        return pipfile.readlines()


with open("requirements.txt", "r", encoding="utf-8") as req_file:
    install_requires = req_file.readlines()

try:
    # Check output
    last_commit: str = subprocess.check_output("git rev-parse --verify --short HEAD", shell=True)
    last_tag_commit: str = subprocess.check_output(
        "git rev-list --tags --max-count=1 --abbrev-commit", shell=True
    )
    tags: str = subprocess.check_output("git rev-list --tags --max-count=1", shell=True)
    last_tag: str = subprocess.check_output("git describe --tags --abbrev=0", shell=True)

    # Strip and Decode
    LAST_COMMIT = last_commit.strip().decode("UTF-8")
    LAST_TAG_COMMIT = last_tag_commit.strip().decode("UTF-8")
    TAGS = tags.strip().decode("UTF-8")
    LAST_TAG = last_tag.strip().decode("UTF-8")

    # Set Version
    if LAST_COMMIT != LAST_TAG_COMMIT:
        # Last Tag's Version + dirty flag
        _VERSION = f"{LAST_TAG}-dirty"
    else:
        # Version is Tag
        _VERSION = LAST_TAG
except subprocess.CalledProcessError:
    # Version is not set
    print(f"WARNING: No Version Set! Using default: {_VERSION}")
except Exception as e:
    print("ERROR: Something happened when trying to set the version: ", e)
    raise e

setup(
    name="pycon",
    description="RCON Communicator Discord Bot",
    version=_VERSION,
    author="Maximilian Stephan",
    author_email="stephan.maxi@icloud.com",
    install_requires=get_requirements(),
    packages=find_packages(exclude=["test", "test.*"]),
    entry_points={"console_scripts": ["pycon = pycon.bin.daemon:main"]},
)
