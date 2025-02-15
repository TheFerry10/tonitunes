import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
import vlc
import os

logger = logging.getLogger(__name__)


class AbstractAudioController(ABC):
    """
    Abstract implementation of a media player.
    """

    @abstractmethod
    def play(self):
        """Play mp3"""

    @abstractmethod
    def pause(self):
        """Pause current song"""

    @abstractmethod
    def stop(self):
        """Stop song when currently playing"""

    @abstractmethod
    def increase_volume(self, step: int):
        """Increase volume by step"""

    @abstractmethod
    def decrease_volume(self, step: int):
        """Decrease volume by step"""


DEFAULT_INSTANCE = vlc.Instance("--aout=alsa")


class VlcAudioController(AbstractAudioController):
    """
    A controller for managing media playback using a single VLC MediaPlayer instance.

    This class allows playing, pausing, resuming, and switching between audio files
    while ensuring efficient use of resources by reusing the same MediaPlayer instance.

    Attributes:
        player (vlc.MediaPlayer): The VLC MediaPlayer instance used for playback.
        current_media_path (str): The file path of the currently loaded media file,
                                  or None if no media is loaded.

    Methods:
        play(file_path):
            Starts or resumes playback of the specified media file.
            If the specified file is different from the currently loaded media,
            the current media is interrupted, and the new file begins playback.

        pause():
            Pauses the current playback if a media file is playing. Does nothing if
            no media is currently playing.

        stop():
            Stops the current playback and resets the media, allowing a new media file
            to be loaded when play() is next called.
    """

    VOLUME = {"min": 0, "max": 100, "default": 75}

    def __init__(self, vlc_instance: vlc.Instance = DEFAULT_INSTANCE):
        self.instance = vlc_instance
        self.playlist = []
        self.media_list = None
        self.list_player = self.instance.media_list_player_new()
        self.player = self.list_player.get_media_player()
        self.player.audio_set_volume(self.VOLUME["default"])

    def load_playlist(self, playlist: List[Path]):
        if playlist == self.playlist:
            logging.info("Playlist already loaded")
        else:
            self.list_player.stop()
            self.playlist = playlist
            self.media_list = self.instance.media_list_new(mrls=playlist)
            self.list_player.set_media_list(self.media_list)
            logging.info("Playlist loaded with %d songs", len(playlist))

    def play(self):
        if self.media_list:
            self.list_player.play()
            logging.info("Playback started")
            self.log_current_media()
        else:
            logging.warning(
                "No playlist loaded. Use load_playlist() to load a playlist"
            )

    def pause(self):
        if self.list_player.is_playing():
            self.list_player.pause()
            logging.info("Song paused")
        else:
            logging.info("No song is currently playing")

    def stop(self):
        if self.list_player.is_playing():
            self.list_player.stop()
            logging.info("Playback stopped")
        else:
            logging.info("No song is currently playing")

    def next(self):
        self.list_player.next()
        logging.info("Next song")
        self.log_current_media()

    def previous(self):
        self.list_player.previous()
        logging.info("Previous song")
        self.log_current_media()

    def increase_volume(self, step: int):
        step = abs(step)
        current_volume = self.player.audio_get_volume()
        if current_volume < self.VOLUME["max"]:
            new_volume = min(current_volume + step, self.VOLUME["max"])
            self.player.audio_set_volume(new_volume)
            logging.info("Volume increased to %d", new_volume)

    def decrease_volume(self, step: int):
        step = abs(step)
        current_volume = self.player.audio_get_volume()
        if current_volume > self.VOLUME["min"]:
            new_volume = max(current_volume - step, self.VOLUME["min"])
            self.player.audio_set_volume(new_volume)
            logging.info("Volume decreased to %d", new_volume)

    def log_current_media(self):
        media = self.player.get_media()
        if media:
            media.parse()
            media_path = media.get_mrl()
            if media_path.startswith("file://"):
                media_path = os.path.basename(media_path)
            logging.info("Currently playing: %s", media_path)
        else:
            logging.info("No media is currently playing")


def is_media_file_valid(file_path: Path) -> bool:
    """Check if the file is a valid media file"""
    valid_file_extensions = (".mp3", ".wav", ".ogg", ".flac")
    if file_path.is_file() and file_path.suffix in valid_file_extensions:
        return True
    else:
        return False
