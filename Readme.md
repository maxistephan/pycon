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

## Testing

Running tests is as easy as using the project itself:

```bash
./run.sh --test
```

To use the docker environment in tests, append the *--docker* option:

```bash
./run.sh --test --docker
```

And to use a specific user in the Docker test environment, the *-g* and *-u* options may help:

```bash
./run.sh --docker -u $(id -u) -g $(id -g) --test
```

**NOTE:** By default, the user ID and Group are the ones from the user starting the script.

**NOTE:** There are currently no tests implemented!

## Important Notice

This Project is set to be in a private repository.
Leaks about source code snippets are completely irrelevant.
The only important part is to keep the **Bot Token** secure,
since the Token is used to control the Bot.

## Developer Info

This project setup to be developed with the VSCode IDE.
Using Pycharm or other IDEs is, of course, also allowed,
if the necessary entries to the *.gitignore* file are added.

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

Make sure to use conventional commits in commit messages!

Testing is done via docker, to assure that test results are valid.

Have fun creating this Bot with me!

~ Maximilian Stephan
