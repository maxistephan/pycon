# PYCON

Discord Bot for RCON Communication implemented in Python.

## Installing

Installing the Bot is rather easy, since it is Python modulized:

```bash
# Clone the sources
git clone https://github.com/maxistephan/pycon.git
cd pycon

# Virtual Environment Setup (skip if unwanted)
sudo apt update && \
    apt install -y --no-install-recommends \
    python3.11 python3.11-dev python3.11-pip python3.11-venv
python3.11 -m venv .venv
. .venv/bin/activate

# Install Dependencies and Project
pip3 install -r requirements.txt
pip3 install -e .
```

## Usage

To get to know about the CLI usage, type this command after installation:

```bash
pycon --help
```

## Important Notice

This Project is set to be in a private repository.
Leaks about source code snippets are completely irrelevant.
The only important part is to keep the **Bot Token** secure,
since the Token is used to control the Bot.

Have fun creating this Bot with me!

~ Maximilian Stephan
