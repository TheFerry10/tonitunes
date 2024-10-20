import base64
import datetime
import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Optional

import RPi.GPIO as GPIO
from azure.storage.queue import QueueClient
from dotenv import load_dotenv
from mfrc522 import SimpleMFRC522

load_dotenv()

queue_url = os.getenv("QUEUE_URL")
queue_client = QueueClient.from_queue_url(queue_url=queue_url)
dummy = {"id": 288367552202, "tag": "101", "timestamp": "2024-10-09T23:22:37.171167"}
message = json.dumps(dummy)
encoded_message = base64.b64encode(message.encode("utf-8")).decode("utf-8")
print(message)
queue_client.send_message(encoded_message)
print("Message sent")
