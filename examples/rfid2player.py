import os
import time
from pathlib import Path

import vlc
from dotenv import load_dotenv
from gpiozero import Button, RotaryEncoder
from RPi import GPIO

from adapters.rfid_interface import ResponseHandler, RFIDResponse, get_action
from app.cardmanager.db import init_db
from app.cardmanager.models import Card
from config import config
from player.player import VlcAudioController
from rfid.mfrc import MFRCModule

load_dotenv(override=True)
CONFIG_NAME = os.getenv("CONFIG_NAME", "default")
Config = config.get(CONFIG_NAME)


AUDIO_DIR = os.environ.get("AUDIO_DIR")
vlc_instance = vlc.Instance("--aout=alsa --loop")
VOLUME_STEP = 5

clk = os.getenv("PIN_CLK")
dt = os.getenv("PIN_DT")
button_pin_next = os.getenv("BUTTON_PIN_NEXT")
button_pin_previous = os.getenv("BUTTON_PIN_PREVIOUS")
encoder = RotaryEncoder(clk, dt, max_steps=0)
button_next = Button(pin=button_pin_next, pull_up=True)
button_previous = Button(pin=button_pin_previous, pull_up=True)
audio_controller = VlcAudioController(vlc_instance)
init_db()


def on_clockwise_rotate():
    audio_controller.increase_volume(VOLUME_STEP)
    print("Current volume ", audio_controller.player.audio_get_volume())


def on_counter_clockwise_rotate():
    audio_controller.decrease_volume(VOLUME_STEP)
    print("Current volume ", audio_controller.player.audio_get_volume())


def on_button_next_pressed():
    audio_controller.next()
    print("Play next song")


def on_button_previous_pressed():
    audio_controller.previous()
    print("Play previous song")


def execute():

    rfid_module = MFRCModule()
    response = RFIDResponse()
    encoder.when_rotated_clockwise = on_clockwise_rotate
    encoder.when_rotated_counter_clockwise = on_counter_clockwise_rotate
    button_next.when_pressed = on_button_next_pressed
    button_previous.when_pressed = on_button_previous_pressed

    try:
        while True:
            response.current = rfid_module.read()
            response_handler = ResponseHandler(response)
            handled_response = response_handler.handle()
            if handled_response:
                controller_action = get_action(handled_response)
                if controller_action.action == "play":
                    print(controller_action.to_dict())
                    card = Card.query.get(controller_action.uid)
                    if card and card.playlist:
                        playlist = [
                            Path(AUDIO_DIR, song.filename)
                            for song in card.playlist.songs
                        ]
                        audio_controller.load_playlist(playlist)
                        audio_controller.play_playlist()
                    else:
                        print("No playlist defined for card")

                elif controller_action.action == "pause":
                    audio_controller.pause()
                    print("Pause")

            response.update()
            time.sleep(3.0)

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
