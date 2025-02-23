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

# should be moved to a separate module
from app.cardmanager.db import db_session, init_db
from config import DevelopmentConfig, config
from player.controller import PlayerActionHandler, rfid_to_player_action
from player.player import VlcAudioController
from rfid.mfrc import MFRCModule


def setup_logger(log_file, level=logging.DEBUG):
    # Create a custom logger
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(log_file)
    c_handler.setLevel(level)
    f_handler.setLevel(level)

    # Create formatters and add them to handlers
    c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    
    return logger

application_config: DevelopmentConfig = config["default"]
volume_step = application_config.player_config.volume_step
vlc_instance_params = application_config.player_config.vlc_instance_params
gpio_config = application_config.gpio_config
vlc_instance = vlc.Instance(vlc_instance_params)
audio_controller = VlcAudioController(vlc_instance)

# rotary_encoder = RotaryEncoder(gpio_config.pin_clk, gpio_config.pin_dt, max_steps=0)
button_next = Button(pin=gpio_config.button_pin_next, pull_up=True)
button_previous = Button(pin=gpio_config.button_pin_previous, pull_up=True)

init_db(application_config.DATABASE_URI)
session = db_session()

def on_clockwise_rotate():
    audio_controller.increase_volume(volume_step)
    print("Current volume ", audio_controller.player.audio_get_volume())


def on_counter_clockwise_rotate():
    audio_controller.decrease_volume(volume_step)
    print("Current volume ", audio_controller.player.audio_get_volume())


def on_button_next_pressed():
    audio_controller.next()
    print("Play next song")


def on_button_previous_pressed():
    audio_controller.previous()
    print("Play previous song")


def start_rfid_player():
    rfid_reader = SimpleMFRC522()
    rfid_module = MFRCModule(reader=rfid_reader)
    repository = SqlAlchemyCardRepositoriy(session=session)
    player_action_handler = PlayerActionHandler(repository)
    handler = ResponseHandler()

    # rotary_encoder.when_rotated_clockwise = on_clockwise_rotate
    # rotary_encoder.when_rotated_counter_clockwise = on_counter_clockwise_rotate
    button_next.when_pressed = on_button_next_pressed
    button_previous.when_pressed = on_button_previous_pressed

    try:
        while True:
            response = rfid_module.read()
            handled_response = handler.handle(response)
            if handled_response:
                player_action = rfid_to_player_action(handled_response)
                audio_controller_command = player_action_handler.handle(player_action)
                audio_controller_command.execute(audio_controller)
                time.sleep(3.0)

    except KeyboardInterrupt:
        print("KeyboardInterrupt detected. Cleaning up...")
    finally:
        GPIO.cleanup()
        print("Cleaning done")


if __name__ == "__main__":
    
    file_name = os.path.splitext(os.path.basename(__file__))[0]
    log_file_path = os.path.join(ROOTDIR, f"logfile-{file_name}.log")
    logger = setup_logger(log_file_path, level=logging.INFO)
    
    start_rfid_player()
