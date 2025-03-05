#!/bin/bash

# Path to the file with placeholders
FILE="tonitunes-default.service"
SERVICE_FILE="tonitunes.service"

# Check if the file exists
if [[ ! -f "$FILE" ]]; then
  echo "File not found: $FILE"
  exit 1
fi

# Replace placeholders with environment variable values
envsubst < "$FILE" > "$SERVICE_FILE"

sudo chmod +x ${PWD}/tonitunes.sh
sudo cp $SERVICE_FILE /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_FILE
sudo systemctl start $SERVICE_FILE
echo "Service ${SERVICE_FILE} started successfully"
