#!/usr/bin env python3

import subprocess

from setuptools import find_packages, setup

_version: str = f"0.0.0-dirty"

try:
    # Check output
    last_commit: str = subprocess.check_output("git rev-parse --verify --short HEAD", shell=True)
    last_tag_commit: str = subprocess.check_output("git rev-list --tags --max-count=1 --abbrev-commit", shell=True)
    tags: str = subprocess.check_output("git rev-list --tags --max-count=1", shell=True)
    last_tag: str = subprocess.check_output("git describe --tags --abbrev=0", shell=True)

    # Strip and Decode
    last_commit = last_commit.strip().decode("UTF-8")
    last_tag_commit = last_tag_commit.strip().decode("UTF-8")
    tags = tags.strip().decode("UTF-8")
    last_tag = last_tag.strip().decode("UTF-8")

    # Set Version
    if last_commit != last_tag_commit:
        # Last Tag's Version + dirty flag
        _version = f"{last_tag}-dirty"
    else:
        # Version is Tag
        _version = last_tag
except subprocess.CalledProcessError:
    # Version is not set
    print(f"WARNING: No Version Set! Using default: {_version}")
except Exception as e:
    print("ERROR: Something happened when trying to set the version: ", e)
    raise e

setup(
    name="pycon",
    description="RCON Communicator Discord Bot",
    version=_version,
    author="Maximilian Stephan",
    author_email="stephan.maxi@icloud.com",
    packages=find_packages(exclude=["test", "test.*"]),
    entry_points={"console_scripts": ["pycon = pycon.bin.daemon:main"]},
)
