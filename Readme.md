# `PYCON`

> Discord Bot for RCON Communication implemented in Python.

## Installation

This bot can be installed as a python pip package.

The `run.sh` script contains the `--install` option to
setup a virtualenv and install the bot:

```bash
# Clone the sources
git clone https://github.com/maxistephan/pycon.git
cd pycon

# Insatll pycon
./run.sh --install

# Start virtual environment (mandatory since 3.11)
python3.11 -m venv .venv
source .venv/bin/activate
```

Or do it manually:

```bash
# Clone the sources
git clone https://github.com/maxistephan/pycon.git
cd pycon

# Install python dependencies
sudo apt install \
    python3.11 \
    python3.11-dev \
    python3.11-pip \
    python3.11-venv

# Start virtual environment (mandatory since 3.11)
python3.11 -m venv .venv
source .venv/bin/activate

# Install Dependencies
pip3 install -r requirements.txt

# Install pycon
pip3 install -e .
```

## Systemd Integration

Currently, pycon only features a simple systemd service:

```bash
# create environment
cat << EOF > <THIS_DIRECTORY>/default.env
PYCON_BOT_TOKEN=tokenfromdiscorddevpage
EOF

# This creates a file called "default.env" in this directory
# with this content:
#   PYCON_BOT_TOKEN=tokenfromdiscorddevpage
#
# Change <THIS_DIRECTORY> to the path of this directory, e.g.
# /home/user/pycon/default.env

# install service
./run.sh --daemonize

# run service
sudo systemctl start pycon

# autostart service at boot
sudo systemctl enable pycon
```

## Usage

```bash
pycon --help
```

## Testing

Tests aren't implemented yet, but in the future the bot will be
tested with the run.sh wrapper as well:

```bash
# Default test
./run.sh --test

# Test in docker container
./run.sh --test --docker

# Test in docker container as current user
./run.sh --docker -u $(id -u) -g $(id -g) --test
```

## Important Notice

The only important part is to keep the **Bot Token** secure,
since the Token is used to control the Bot.

The run.sh script has the option to implement a `default.env` file
with custom env variables, that are sourced by the systemd service as
well.

## Developer Info

Pip requirements are defined in requirements.in and requirements-test.in.
The `pip-compile` command is used to create requirements.txt and requirements-test.txt:

```bash
# Create requirements.txt
pip-compile requirements.in

# Create requirements-test.txt
pip-compile requirements-test.in
```

Install pip tools for this matter:

```bash
python3 -m pip install pip-tools
```

Testing will be done via docker to minimize dependency issues.

Have fun developing this Bot with me!
