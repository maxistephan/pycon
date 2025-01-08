#!/bin/bash

set -e
[ "$DEBUG" = "1" ] && set -x

function print_help() {
    echo "Helper Script to run tests for pycon."
    echo
    echo "Usage:"
    echo "------"
    echo "  > $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "--------"
    echo "     --docker           Use the Docker Environment."
    echo "  -g|--gid GROUP_ID     Use a specific Group ID for the Docker user."
    echo "  -h|--help             Print this text to help with the usage."
    echo "     --install          Install pycon in virtualenv at '$THISDIR/.venv'."
    echo "     --test             Run tests for pycon."
    echo "  -t|--token BOT_TOKEN  Bot token. Can also be passed via env PYCON_BOT_TOKEN."
    echo "  -u|--uid USER_ID      Use a specific User ID for the Docker user."
    echo
    echo "Examples:"
    echo "---------"
    echo "Run tests without using Docker."
    echo " > $0 --test"
    echo
    echo "Run tests in Docker container."
    echo " > $0 --docker --test"
    echo
    echo "Install pycon and daemonize it."
    echo " > $0 --install --daemonize"
}

function is_venv() {
    PYTHON_EXEC="$(which python3)"
    case $PYTHON_EXEC/ in
        $THISDIR/*)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

function source_venv() {
    if [ -d "$THISDIR/.venv" ]; then
        source $THISDIR/.venv/bin/activate
    else
        echo "ERROR: No virtualenv found."
        return 1
    fi
}

function create_venv() {
    local rec="${1:-0}"
    is_venv && return 0

    if [ ! -d "$THISDIR/.venv" ]; then
        if [ "$rec" = "1" ]; then
            echo "ERROR: could not create venv.";
            return 1
        fi
        echo "Creating python virtualenv"
        python3.11 -m venv "$THISDIR/.venv" || (
            echo "WARNING: python3.11 not found. Trying default python3 ...";
            python3 -m venv "$THISDIR/.venv"
        )
        # Call recursively to check if venv creation succeeded.
        create_venv "1"
    fi
}

function install_deps() {
    # Install python deps
    pip install -r "${THISDIR}/requirements.txt"
}

function install_pycon() {
    # This has to be set again to fail correctly
    set -e

    # Early return if already installed
    if [ -n "$(which pycon)" ]; then
        return 0
    fi
    
    # Venv
    create_venv
    source_venv
    install_deps

    # Install pycon
    pip install -e "$THISDIR"

    # Test if the installation worked
    if [ -z "$(which pycon)" ]; then
        echo "ERROR: pycon installation failed."
        return 1
    fi

    echo "pycon installation complete!"
    echo "Run 'source $THISDIR/.venv/bin/activate' to activate virtualenv and run pycon."
}

function remove_temp_sed() {
    rm -f "$THISDIR/.tmp.service"
}

function daemonize_pycon() {
    local pycon_systemd_service_f="/lib/systemd/system/pycon.service"
    if [ -f "$pycon_systemd_service_f" ]; then
        echo "pycon is already daemonized. Use 'systemctl start pycon' to start the service."
        return 0
    fi

    cp "$THISDIR/pycon.service" "$THISDIR/.tmp.service" 2>&1

    sed -i "s|__PYCON_INSTALL_DIR__|$THISDIR|g" "$THISDIR/.tmp.service"

    set +e
    trap remove_temp_sed EXIT
    cp -v "$THISDIR/.tmp.service" "$pycon_systemd_service_f"

    if [ $? -ne 0 ]; then
        if [ 0 -ne $(id -u) ]; then
            echo "WARNING: current user is not root. Retrying copy with sudo ..."
        else
            echo "ERROR: Could not copy service file to $pycon_systemd_service_f. Are you using systemd?"
            return 1
        fi
        sudo cp -v "$THISDIR/.tmp.service" "$pycon_systemd_service_f"
    fi
    set -e
    remove_temp_sed

    echo "Pycon is now daemonized. Use 'systemctl start pycon' to start the service."
}

# Detemine this scripts path
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    *)          machine="${unameOut}"
esac

echo "Detected System: $machine"

if [ "$machine" = "Mac" ]; then
    THISDIR="$(dirname $(readlink -f $0))"
else
    THISDIR="$(dirname $(readlink -e -- $0))"
fi

# Load environment from a file, if available
if [ -f "$THISDIR/default.env" ]; then
  source $THISDIR/default.env
fi

DOCKER_ARGS=
BOT_ARGS=

while [ $# -gt 0 ]; do
    case $1 in
        --daemonize)
            daemonize_pycon
            shift
            ;;
        --docker)
            USE_DOCKER="1"
            shift
            ;;
        -g|--gid)
            GROUP_ID=$2
            DOCKER_ARGS+=" $1 $2"
            shift 2
            ;;
        -h|--help)
            print_help
            exit 0
            ;;
        --install)
            PYCON_INSTALL="1"
            DOCKER_ARGS+=" $1"
            shift
            ;;
        --test)
            RUN_TESTS="1"
            DOCKER_ARGS+=" $1"
            shift
            ;;
        -t|--token)
            PYCON_BOT_TOKEN="$2"
            DOCKER_ARGS+=" $1 $2"
            shift 2
            ;;
        --run-bot)
            RUN_BOT="1"
            DOCKER_ARGS+=" $1"
            shift
            ;;
        -u|--uid)
            USER_ID=$2
            DOCKER_ARGS+=" $1 $2"
            shift 2
            ;;
        -*)
            echo "Unknown Option."
            print_help
            exit 1
            ;;
        *)
            echo "Unknown Argument."
            print_help
            exit 1
    esac
done

BOT_ARGS+=" ${PYCON_BOT_TOKEN:+--token $PYCON_BOT_TOKEN} "

if [ -n "${USE_DOCKER}" ]; then
    USER_ID=${USER_ID:-$(id -u)} GROUP_ID=${GROUP_ID:-$(id -g)} \
        docker compose \
            -f docker/compose.yml \
            run --rm pycon-env \
            ./run.sh $DOCKER_ARGS
    exit 0
fi

if [ "$PYCON_INSTALL" = "1" ]; then
    install_pycon
fi

if [ -n "${RUN_TESTS}" ]; then
    echo "No testing environment implemented yet!"
fi

# Source virtualenv before start, if pycon command does not exist.
PYCON_PATH="${PYCON_PATH:-$(which pycon)}" || true

if [ -z "$PYCON_PATH" ]; then
    echo "pycon not found in PATH. Trying virtualenv ..."
    if [ -d "$THISDIR/.venv" ]; then
        source $THISDIR/.venv/bin/activate
    else
        echo "ERROR: No virtualenv found."
        exit 1
    fi
    PYCON_PATH="${PYCON_PATH:-$(which pycon)}"
fi

if [ -n "${RUN_BOT}" ]; then
    echo "Starting the Bot ..."
    $PYCON_PATH $BOT_ARGS
fi
