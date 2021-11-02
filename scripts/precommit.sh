#!/bin/bash

set -e

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT_DIR="$SCRIPT_DIR/.."

cd "${ROOT_DIR}"
shellcheck -x start.sh
shellcheck -x scripts/precommit.sh
shellcheck -x scripts/setup.sh
# shellcheck source=/dev/null
source .venv/bin/activate
autopep8 --in-place --aggressive ./*.py
autopep8 --in-place --aggressive bot/*.py
autopep8 --in-place --aggressive util/*.py
isort .

echo "Done!"