import os
import time
from pathlib import Path

from dotenv import load_dotenv

from player.player import VlcAudioController

load_dotenv(override=True)

AUDIO_DIR = os.getenv("AUDIO_DIR")
audio_controller = VlcAudioController()
file_path = Path(AUDIO_DIR, "Kinderlieder-Superstar - Große Uhren machen tick tack.mp3")
playlist_1 = [
    Path(AUDIO_DIR, "Volker Rosin - Die Laternenzeit.mp3"),
    Path(AUDIO_DIR, "Volker Rosin - Dino Tanz.mp3"),
]


playlist_2 = [
    Path(AUDIO_DIR, "Volker Rosin - Music Man.mp3"),
    Path(AUDIO_DIR, "Volker Rosin - Oakie Doakie.mp3"),
]


audio_controller.load_playlist(playlist_1)
audio_controller.play_playlist()
time.sleep(3)
audio_controller.pause()
time.sleep(3)
audio_controller.load_playlist(playlist_1)
audio_controller.play_playlist()
time.sleep(4)
audio_controller.pause()
time.sleep(3)
audio_controller.load_playlist(playlist_2)
audio_controller.play_playlist()
time.sleep(4)
audio_controller.next()
time.sleep(4)
audio_controller.pause()
time.sleep(3)
