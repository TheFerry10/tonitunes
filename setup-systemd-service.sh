#!/bin/bash
#
# This script sets up and starts a systemd service based on a provided service file blueprint.
#
# Usage: ./setup-systemd-service.sh <SERVICE_FILE_BLUEPRINT> [EXEC_BASH_SCRIPT]
#
# Arguments:
#   SERVICE_FILE_BLUEPRINT: The blueprint file for the service (must end with '-default.service').
#   EXEC_BASH_SCRIPT: Optional. The executable bash script to be associated with the service. If not provided,
#                     it defaults to the service file name with '.sh' extension.
#
# The script performs the following steps:
# 1. Validates the input arguments.
# 2. Checks if the provided service file blueprint exists and has a valid name.
# 3. Determines the service file name by removing '-default' from the blueprint name.
# 4. Determines the executable bash script name if not provided.
# 5. Checks if the executable bash script exists.
# 6. Replaces placeholders in the service file blueprint with environment variable values.
# 7. Makes the executable bash script executable.
# 8. Copies the service file to the systemd system directory.
# 9. Reloads the systemd daemon, enables, and starts the service.
#
# Example:
#   ./setup-systemd-service.sh tonitunes-default.service tonitunes.sh
#
# Note:
# - Ensure you have the necessary permissions to execute this script and manage systemd services.

if [[ -z "$1" ]]; then
    echo "Usage: $0 <SERVICE_SERVICE_FILE_BLUEPRINT_BLUEPRINT> [EXEC_BASH_SCRIPT]"
    exit 1
fi


SERVICE_FILE_BLUEPRINT="$1"

if [[ ! -f $SERVICE_FILE_BLUEPRINT ]]; then
  echo "File not found: $SERVICE_FILE_BLUEPRINT"
  exit 1
fi

if [[ $SERVICE_FILE_BLUEPRINT != *-default.service ]]; then
    echo "Invalid service file name: $SERVICE_FILE_BLUEPRINT"
    exit 1
fi

SERVICE_FILE="${SERVICE_FILE_BLUEPRINT/-default/}"

if [[ -n "$2" ]]; then
    EXEC_SERVICE_FILE_BLUEPRINT="$2"
else
    EXEC_SERVICE_FILE_BLUEPRINT="${SERVICE_FILE/.service/.sh}"
fi

if [[ ! -f $EXEC_SERVICE_FILE_BLUEPRINT ]]; then
  echo "File not found: $EXEC_SERVICE_FILE_BLUEPRINT"
  exit 1
fi


echo "Service file: $SERVICE_FILE"
echo "Exec file: $EXEC_SERVICE_FILE_BLUEPRINT"

# Replace placeholders with environment variable values
envsubst < "$SERVICE_FILE_BLUEPRINT" > "$SERVICE_FILE"

sudo chmod +x $EXEC_SERVICE_FILE_BLUEPRINT
sudo cp $SERVICE_FILE /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_FILE
sudo systemctl start $SERVICE_FILE
echo "Service ${SERVICE_FILE} started successfully"
