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
cp $SERVICE_FILE /etc/systemd/system/

systemctl daemon-reload
systemctl enable $SERVICE_FILE
systemctl start $SERVICE_FILE
echo "Service started successfully"
