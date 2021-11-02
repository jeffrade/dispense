#!/bin/bash

set -e

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT_DIR="$SCRIPT_DIR/.."

echo "Starting..."

mkdir -p "${ROOT_DIR}/tmp" && chmod 777 "${ROOT_DIR}/tmp/"
mkdir -p "${ROOT_DIR}/slack_teams"
sudo apt update
sudo apt install -y python3-pip python3.8-venv sqlite3 shellcheck
cd "${ROOT_DIR}"
python3 -m venv .venv
pip install cacheout # https://github.com/dgilland/cacheout
pip install slack_bolt
pip install --upgrade autopep8
pip install isort

GLOBAL_DB="${ROOT_DIR}/slack_teams/global.db"
if [ ! -f "${GLOBAL_DB}" ]; then
    sqlite3 "${GLOBAL_DB}" < "${SCRIPT_DIR}/setup.sql"
fi

echo "Complete!"
