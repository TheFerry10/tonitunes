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

load_dotenv()


SLEEP_TIME_BETWEEN_READS_IN_SECONDS = 0.5
queue_url = os.getenv("QUEUE_URL_LOCAL")
queue_client = QueueClient.from_queue_url(queue_url=queue_url)


@dataclass
class RFIDResponse:
    id: int
    tag: str
    timestamp: datetime.datetime


def check_different_request(
    current: RFIDResponse, last: Optional[RFIDResponse]
) -> bool:
    id_tag_condition = (last.id != current.id) | (last.tag != current.tag)
    return id_tag_condition


def check_retry_request(
    current: RFIDResponse,
    last: Optional[RFIDResponse],
    TIME_DELTA_THRESHOLD_SECONDS: int = 5,
) -> bool:
    time_delta_threshold = datetime.timedelta(seconds=TIME_DELTA_THRESHOLD_SECONDS)
    id_tag_condition = (last.id == current.id) & (last.tag == current.tag)
    timestamp_condition = (current.timestamp - last.timestamp) > time_delta_threshold
    return id_tag_condition & timestamp_condition


def check_responses(current: RFIDResponse, last: Optional[RFIDResponse]) -> bool:
    if last_response:
        return check_different_request(current, last) | check_retry_request(
            current, last
        )
    else:
        return True


def convert_dataclass_to_json(dataclass_: dataclass) -> str:
    dataclass_as_dictionary = asdict(dataclass_)

    def converter(field):
        if isinstance(field, datetime.datetime):
            return field.isoformat()
    message_json = json.dumps(dataclass_as_dictionary, default=converter)
    return message_json.encode('utf-8')

response = None
last_response = None
reader = SimpleMFRC522()
try:
    while True:
        id, text = reader.read()
        timestamp = datetime.datetime.now()
        response = RFIDResponse(id=id, tag=text.strip(), timestamp=timestamp)
        if check_responses(current=response, last=last_response):
            # message = convert_dataclass_to_json(response)
            message = json.dumps({"id": 288367552202, "tag": "101", "timestamp": "2024-10-09T23:22:37.171167"})
            print(message)
            queue_client.send_message(message)
            print("Message sent")
        last_response = response
        time.sleep(SLEEP_TIME_BETWEEN_READS_IN_SECONDS)
except KeyboardInterrupt:
    print("KeyboardInterrupt detected. Cleaning up...")
finally:
    GPIO.cleanup()
    print("Cleaning done")
