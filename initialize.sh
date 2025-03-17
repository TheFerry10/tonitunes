#!/bin/bash
# This script initializes the directory structure and environment variables for the ToniTunes project.
# It performs the following tasks:
# 1. Defines the TONITUNES_HOME directory and subdirectories (songs, cards, sqlite).
# 2. Creates the subdirectories under TONITUNES_HOME if they do not already exist.
# 3. Adds the TONITUNES_HOME environment variable to the .bashrc file if it is not already present.
# 4. Sources the .bashrc file to apply the changes.

TONITUNES_HOME="${HOME}/.tonitunes"
SUB_DIRS=("songs" "cards" "sqlite")
BASHRC_FILE="${HOME}/.bashrc"
ENV_VAR_EXPORT="export TONITUNES_HOME=${TONITUNES_HOME}"

# create directory
for sub_dir in "${SUB_DIRS[@]}"; do
    sub_dir_path="${TONITUNES_HOME}/${sub_dir}"
    if [ -d "$sub_dir_path" ]; then
        echo "Subdirectory ${sub_dir} already exists"
    else
        mkdir -p "$sub_dir_path"
        echo "Subdirectory ${sub_dir} created at ${sub_dir_path}"
    fi
done
echo "TONITUNES_HOME directory present at ${TONITUNES_HOME}"

# set environment variables
if ! grep -Fxq "${ENV_VAR_EXPORT}" "${BASHRC_FILE}"; then
    echo "# ToniTunes project" >> "$BASHRC_FILE"
    echo "$ENV_VAR_EXPORT" >> "$BASHRC_FILE"
else
    echo "${ENV_VAR_EXPORT} is already present in ${BASHRC_FILE}"
fi
source ${BASHRC_FILE}
