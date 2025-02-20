import json
import os
import time
from pathlib import Path

import vlc
from dotenv import load_dotenv
from gpiozero import Button, RotaryEncoder
from mfrc522 import SimpleMFRC522
from RPi import GPIO

from adapters.rfid_interface import ResponseHandler, RFIDResponse, get_action

# should be moved to a separate module
from app.cardmanager.db import init_db
from app.cardmanager.models import Card
from player.player import VlcAudioController
from rfid.mfrc import MFRCModule

# loading environment variables from .env file not optimal
load_dotenv(override=True)
clk = os.getenv("PIN_CLK")
dt = os.getenv("PIN_DT")
button_pin_next = os.getenv("BUTTON_PIN_NEXT")
button_pin_previous = os.getenv("BUTTON_PIN_PREVIOUS")
audio_dir = os.environ.get("AUDIO_DIR")


with open("settings.json") as f:
    settings = json.load(f)
player_config = settings["player"]
vlc_instance_params = player_config.get("vlc_instance_params", "")
volume_step = player_config.get("volume_step", 5)


vlc_instance = vlc.Instance(vlc_instance_params)
audio_controller = VlcAudioController(vlc_instance)

rotary_encoder = RotaryEncoder(clk, dt, max_steps=0)
button_next = Button(pin=button_pin_next, pull_up=True)
button_previous = Button(pin=button_pin_previous, pull_up=True)
init_db()


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


def handle_play_action(controller_action, audio_controller, audio_dir):
    print(controller_action.to_dict())
    card = Card.query.get(controller_action.uid)
    if card and card.playlist:
        playlist = [Path(audio_dir, song.filename) for song in card.playlist.songs]
        audio_controller.load_playlist(playlist)
        audio_controller.play_playlist()
    else:
        print("No playlist defined for card")


def handle_pause_action(audio_controller):
    audio_controller.pause()
    print("Pause")


def execute():
    rfid_reader = SimpleMFRC522()
    rfid_module = MFRCModule(reader=rfid_reader)
    response = RFIDResponse()
    rotary_encoder.when_rotated_clockwise = on_clockwise_rotate
    rotary_encoder.when_rotated_counter_clockwise = on_counter_clockwise_rotate
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
                    handle_play_action(controller_action, audio_controller, audio_dir)
                elif controller_action.action == "pause":
                    handle_pause_action(audio_controller)

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
