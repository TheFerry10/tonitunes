import os

from dotenv import load_dotenv
from RPi import GPIO

from adapters.rfid_interface import ResponseHandler, RFIDResponse, get_action
from config import config
from rfid.mfrc import MFRCModule


class FakeQueueClient:
    def __init__(self):
        self.queue = []

    def send_message(self, message):
        """Simulate sending a message to the queue."""
        self.queue.append(message)
        return True

    def receive_message(self):
        """Simulate receiving a message from the queue."""
        if self.queue:
            return self.queue.pop(0)
        return None

    def get_queue_length(self):
        """Returns the number of messages in the queue."""
        return len(self.queue)

    def clear_messages(self):
        self.queue = []


load_dotenv(override=True)
CONFIG_NAME = os.getenv("CONFIG_NAME", "default")
Config = config.get(CONFIG_NAME)
rfid_module = MFRCModule()
queue_client = FakeQueueClient()
queue_client.clear_messages()

response = RFIDResponse()

try:
    while True:
        response.current = rfid_module.read()
        response_handler = ResponseHandler(response)
        handled_response = response_handler.handle()
        if handled_response:
            action = get_action(handled_response)
            message_json = action.to_json()
            queue_client.send_message(message_json)
            print(message_json)
        response.update()
except KeyboardInterrupt:
    print("KeyboardInterrupt detected. Cleaning up...")
finally:
    GPIO.cleanup()
    print("Cleaning done")
