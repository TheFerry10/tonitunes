import time

from RPi import GPIO

from src.adapters.rfid_interface import RFIDResponse, get_action, handle_response
from src.config import config
from src.rfid.mfrc import MFRCModule
from tests.test_rfid import FakeQueueClient

Config = config.get("development")
rfid_module = MFRCModule()
queue_client = FakeQueueClient()
queue_client.clear_messages()

response = RFIDResponse()
while True:
    try:
        response.current = rfid_module.read()
        # NOTE ResponseHandler should be an object
        handled_response = handle_response(response)
        # NOTE this can be encapsulated
        if handled_response:
            action = get_action(handled_response)
            message_json = action.to_json()
            queue_client.send_message(message_json)
        response.update()
        time.sleep(Config.SLEEP_TIME_BETWEEN_READS_IN_SECONDS)
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected. Cleaning up...")
    finally:
        GPIO.cleanup()
        print("Cleaning done")
