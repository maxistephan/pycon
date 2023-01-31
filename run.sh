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
    echo "     --test             Run tests for pycon."
    echo "  -u|--uid USER_ID      Use a specific User ID for the Docker user."
    echo ""
    echo "Examples:"
    echo "---------"
    echo " > $0 --test"
    echo " This command runs tests for the pycon bot without using Docker."
    echo
    echo " > $0 --docker --test"
    echo " This command runs tests inside a docker container."
    echo
    echo " > $0 --uid 1000 --gid 1000 --docker --test"
    echo " This command runs tests inside a docker container, as user '1000:1000'."
}

DOCKER_ARGS=

while [ $# -gt 0 ]; do
    case $1 in
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
        --test)
            RUN_TESTS="1"
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

if [ -n "${USE_DOCKER}" ]; then
    USER_ID=${USER_ID:-$(id -u)} GROUP_ID=${GROUP_ID:-$(id -g)} \
        docker compose \
            -f docker/compose.yml \
            run --rm pycon-env \
            ./run.sh $DOCKER_ARGS
    exit 0
fi

if [ -n "${RUN_TESTS}" ]; then
    echo "No testing environment implemented yet!"
    exit 1
fi
