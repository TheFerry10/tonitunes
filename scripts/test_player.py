import os
import time
from pathlib import Path
from typing import List, Union
from dotenv import load_dotenv
import logging
from player.player import VlcAudioController, is_media_file_valid

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

load_dotenv("/home/malte/Dokumente/projects/tonibox-rfid/.env", override=True)


file_path_song_1 = os.environ["VALID_FILE_PATH_SONG_1"]
file_path_song_2 = os.environ["VALID_FILE_PATH_SONG_2"]
file_path_song_3 = os.environ["VALID_FILE_PATH_SONG_3"]
invalid_file_path_song = os.environ["INVALID_FILE_PATH_SONG"]


def create_playlist(file_paths: List[Union[Path, str]]) -> List[Path]:
    playlist = []
    for file_path in file_paths:
        if is_media_file_valid(Path(file_path)):
            playlist.append(Path(file_path))
        else:
            raise ValueError(f"Invalid file path: {file_path}")
    return playlist


# playlist_1 = create_playlist([file_path_song_1, file_path_song_2])
# playlist_2 = create_playlist([file_path_song_3])

playlist_1 = create_playlist(
    [
        "tests/resources/music_sample_1.mp3",
        "tests/resources/music_sample_2.mp3",
    ]
)
playlist_2 = create_playlist(
    [
        "tests/resources/music_sample_3.mp3",
        "tests/resources/music_sample_4.mp3",
    ]
)

audio_controller = VlcAudioController()

audio_controller.load_playlist(playlist_1)
audio_controller.play()
time.sleep(2)
audio_controller.pause()
time.sleep(2)
audio_controller.play()
time.sleep(2)
audio_controller.next()
time.sleep(2)
audio_controller.previous()
time.sleep(2)
audio_controller.load_playlist(playlist_2)
audio_controller.play()
time.sleep(2)
audio_controller.stop()
