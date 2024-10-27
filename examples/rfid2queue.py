import os

from dotenv import load_dotenv
from RPi import GPIO

from src.adapters.rfid_interface import ResponseHandler, RFIDResponse, get_action
from src.config import config
from src.rfid.mfrc import MFRCModule
from tests.test_rfid import FakeQueueClient

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
