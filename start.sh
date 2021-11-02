#!/bin/bash

set -e

conf_dirs=()
while IFS='' read -r line; do conf_dirs+=("$line"); done < <(find "$PWD/slack_teams" -type d)

for conf_dir in "${conf_dirs[@]}"; do
    conf_file="${conf_dir}/dispense.conf"
    if [[ -f "$conf_file" ]]; then
        echo "Found $conf_file, starting..."
        nohup python3 main.py "${conf_file}" > dispense.log 2>&1 &
        echo "$!" > "${conf_dir}/dispense.pid"
    fi
done
