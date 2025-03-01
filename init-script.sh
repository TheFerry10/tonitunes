#!/bin/bash
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
