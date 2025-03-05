import time
import os
import vlc
from gpiozero import Button, RotaryEncoder
from mfrc522 import SimpleMFRC522
from RPi import GPIO
import logging
from config import ROOTDIR

from adapters.repository import SqlAlchemyCardRepositoriy
from adapters.rfid_interface import ResponseHandler

from app.cardmanager.db import db_session, init_db
from config import DevelopmentConfig, config
from player.controller import PlayerActionHandler, rfid_to_player_action
from player.player import VlcAudioController
from rfid.mfrc import MFRCModule


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
config_name = os.getenv("TONITUNES_CONFIG_NAME", "default")
application_config: DevelopmentConfig = config.get(config_name)
application_settings = application_config.SETTINGS

volume_step = application_settings.getint("player", "volume_step")
vlc_instance_params = application_settings.get("player", "vlc_instance_params")
gpio_settings = application_settings["gpio"]


vlc_instance = vlc.Instance(vlc_instance_params)
audio_controller = VlcAudioController(vlc_instance)

rotary_encoder = RotaryEncoder(
    gpio_settings.getint("pin_clk"), gpio_settings.getint("pin_dt"), max_steps=0
)
button_next = Button(pin=gpio_settings.getint("button_pin_next"), pull_up=True)
button_previous = Button(pin=gpio_settings.getint("button_pin_previous"), pull_up=True)

init_db(application_config.DATABASE_URI)
session = db_session()


def on_clockwise_rotate():
    audio_controller.increase_volume(volume_step)
    logging.info(f"Current volume {audio_controller.player.audio_get_volume()}")


def on_counter_clockwise_rotate():
    audio_controller.decrease_volume(volume_step)
    logging.info(f"Current volume {audio_controller.player.audio_get_volume()}")


def on_button_next_pressed():
    audio_controller.next()
    logging.info("Play next song")


def on_button_previous_pressed():
    audio_controller.previous()
    logging.info("Play previous song")


def start_rfid_player():
    rfid_reader = SimpleMFRC522()
    rfid_module = MFRCModule(reader=rfid_reader)
    repository = SqlAlchemyCardRepositoriy(session=session)
    player_action_handler = PlayerActionHandler(repository)
    handler = ResponseHandler()

    rotary_encoder.when_rotated_clockwise = on_clockwise_rotate
    rotary_encoder.when_rotated_counter_clockwise = on_counter_clockwise_rotate
    button_next.when_pressed = on_button_next_pressed
    button_previous.when_pressed = on_button_previous_pressed
    
    logging.info("TONITUNES running. Hold your RFID card near the reader.")
    try:
        while True:
            response = rfid_module.read()
            handled_response = handler.handle(response)
            if handled_response:
                player_action = rfid_to_player_action(handled_response)
                audio_controller_command = player_action_handler.handle(player_action)
                audio_controller_command.execute(audio_controller)
                time.sleep(
                    application_settings.getfloat(
                        "rfid-reader", "timeout_between_reads_in_seconds"
                    )
                )

    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt detected. Cleaning up...")
    finally:
        GPIO.cleanup()
        logging.info("Cleaning done")


if __name__ == "__main__":

    start_rfid_player()
