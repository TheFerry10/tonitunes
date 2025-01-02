import os
import time
from pathlib import Path
from player.player import VlcAudioController


AUDIO_DIR = os.getenv("AUDIO_DIR")
audio_controller = VlcAudioController()
file_path = Path(AUDIO_DIR, "Kinderlieder-Superstar - Große Uhren machen tick tack.mp3")
playlist = [
    Path(AUDIO_DIR, "Kinderlieder-Superstar - Große Uhren machen tick tack.mp3"),
    Path(AUDIO_DIR, "Kinderlieder-Superstar - Die Räder vom Bus.mp3"),
    Path(AUDIO_DIR, "Kinderlieder-Superstar - Laterne, Laterne.mp3"),
    Path(AUDIO_DIR, "Kinderlieder-Superstar - Zehn kleine Zappelmänner.mp3"),
]
audio_controller.load_playlist(playlist)
audio_controller.play(playlist[0])
time.sleep(3)
audio_controller.play_next()
time.sleep(3)
audio_controller.play_previous()
time.sleep(3)
audio_controller.play_next()
time.sleep(3)
audio_controller.play_next()
time.sleep(3)
audio_controller.play_next()
time.sleep(3)
audio_controller.play_next()
time.sleep(3)
