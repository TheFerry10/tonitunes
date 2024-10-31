import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

import vlc

logger = logging.getLogger(__name__)


class AbstractAudioController(ABC):
    """
    Abstract implementation of a media player.
    """

    @abstractmethod
    def play(self, file_path):
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

    def __init__(self):
        self.player = vlc.MediaPlayer()
        self.current_media_path = None
        self.player.audio_set_volume(self.VOLUME["default"])

    def play(self, file_path: Union[Path, str]):

        if file_path == self.current_media_path:

            if not self.player.is_playing():
                self.player.play()
                logging.info("Resume with filepath %s", file_path)
            else:
                logging.info("Already playing %s", file_path)

        else:
            self.current_media_path = file_path
            media = vlc.Media(file_path)
            self.player.set_media(media)
            self.player.play()
            logging.info("Play the new song %s", file_path)

    def pause(self):
        if self.player.is_playing():
            self.player.pause()
            logging.info("Song paused")
        else:
            logging.info("No song is currently playing")

    def stop(self):
        self.player.stop()
        logging.info("Playback stopped")
        self.current_media_path = None

    def increase_volume(self, step: int):
        step = abs(step)
        current_volume = self.player.audio_get_volume()
        if current_volume < self.VOLUME["max"]:
            new_volume = min(current_volume + step, self.VOLUME["max"])
            self.player.audio_set_volume(new_volume)

    def decrease_volume(self, step: int):
        step = abs(step)
        current_volume = self.player.audio_get_volume()
        if current_volume > self.VOLUME["min"]:
            new_volume = max(current_volume - step, self.VOLUME["min"])
            self.player.audio_set_volume(new_volume)
