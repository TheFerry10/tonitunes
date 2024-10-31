import os

from dotenv import load_dotenv
from RPi import GPIO

from adapters.rfid_interface import ResponseHandler, RFIDResponse, get_action
from config import config
from player.player import VlcAudioController
from rfid.mfrc import MFRCModule
from utils.mapper import FilePathMapper

load_dotenv(override=True)
CONFIG_NAME = os.getenv("CONFIG_NAME", "default")
Config = config.get(CONFIG_NAME)


AUDIO_DIR = os.environ.get("AUDIO_DIR")
MEDIA_MAPPING_PATH = os.environ.get("MEDIA_MAPPING_PATH")


file_path_mapper = FilePathMapper(
    media_mapping_path=MEDIA_MAPPING_PATH, audio_dir=AUDIO_DIR
)


def execute():

    rfid_module = MFRCModule()
    response = RFIDResponse()
    audio_controller = VlcAudioController()

    try:
        while True:
            response.current = rfid_module.read()
            response_handler = ResponseHandler(response)
            handled_response = response_handler.handle()
            if handled_response:
                controller_action = get_action(handled_response)
                if controller_action.action == "play":
                    file_path = "song.mp3"
                    audio_controller.play(file_path)

                elif controller_action.action == "pause":
                    audio_controller.pause()

            response.update()

    except KeyboardInterrupt:
        print("KeyboardInterrupt detected. Cleaning up...")
    finally:
        GPIO.cleanup()
        print("Cleaning done")


if __name__ == "__main__":
    try:
        execute()
    except KeyboardInterrupt:
        print("Stopping queue listener.")
