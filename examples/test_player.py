import os
import time
from pathlib import Path

import pygame

AUDIO_DIR = os.getenv("AUDIO_DIR")
id_to_filename = {
    "100": "Kinderlieder-Superstar - Große Uhren machen tick tack.mp3",
    "101": "Kinderlieder-Superstar - Die Räder vom Bus.mp3",
    "102": "Kinderlieder-Superstar - Laterne, Laterne.mp3",
    "103": "Kinderlieder-Superstar - Zehn kleine Zappelmänner.mp3",
}
audio_file_path = Path(AUDIO_DIR, id_to_filename["101"])
if audio_file_path.exists():
    print("file existis: ", audio_file_path)

# Initialize pygame mixer
pygame.mixer.init()
pygame.mixer.music.load(audio_file_path)
pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    time.sleep(1)
