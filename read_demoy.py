import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from dataclasses import dataclass, asdict
import datetime
import time
import os
from azure.storage.queue import QueueClient
import json
from typing import Optional
from dotenv import load_dotenv
import base64

load_dotenv()

queue_url = os.getenv("QUEUE_URL")
queue_client = QueueClient.from_queue_url(queue_url=queue_url)
dummy = {"id": 288367552202, "tag": "101", "timestamp": "2024-10-09T23:22:37.171167"}
message = json.dumps(dummy)
encoded_message = base64.b64encode(message.encode("utf-8")).decode("utf-8")
print(message)
queue_client.send_message(encoded_message)
print("Message sent")
