import pytest
from unittest.mock import patch
from pathlib import Path
from player.player import VlcAudioController, is_media_file_valid
import time
import logging
from typing import List, Union


def create_playlist(file_paths: List[Union[Path, str]]) -> List[Path]:
    playlist = []
    for file_path in file_paths:
        if is_media_file_valid(Path(file_path)):
            playlist.append(Path(file_path))
        else:
            raise ValueError(f"Invalid file path: {file_path}")
    return playlist


@pytest.fixture
def mock_vlc_instance():
    with patch("player.player.vlc.Instance") as mock_instance:
        yield mock_instance.return_value


@pytest.fixture
def audio_controller(mock_vlc_instance):
    return VlcAudioController(vlc_instance=mock_vlc_instance)


def test_loading_an_existing_playlist(audio_controller):
    existing_playlist = [Path("sample1.mp3"), Path("sample2.mp3")]
    audio_controller.playlist = existing_playlist
    audio_controller.load_playlist(existing_playlist)
    audio_controller.list_player.set_media_list.assert_not_called()


def test_loading_a_new_playlist(audio_controller):
    new_playlist = [Path("sample1.mp3"), Path("sample2.mp3")]
    audio_controller.load_playlist(new_playlist)
    audio_controller.list_player.set_media_list.assert_called_once_with(
        audio_controller.media_list
    )


def test_playing_with_media_loaded(audio_controller):
    audio_controller.load_playlist([Path("sample1.mp3"), Path("sample2.mp3")])
    audio_controller.play()
    audio_controller.list_player.play.assert_called_once()


def test_playing_without_media_loaded(audio_controller):
    audio_controller.play()
    audio_controller.list_player.play.assert_not_called()


def test_pausing_when_playing(audio_controller):
    audio_controller.list_player.is_playing.return_value = True
    audio_controller.pause()
    audio_controller.list_player.pause.assert_called_once()


def test_pausing_when_not_playing(audio_controller):
    audio_controller.list_player.is_playing.return_value = False
    audio_controller.pause()
    audio_controller.list_player.pause.assert_not_called()


def test_stopping(audio_controller):
    audio_controller.stop()
    audio_controller.list_player.stop.assert_called_once()


def test_next(audio_controller):
    audio_controller.next()
    audio_controller.list_player.next.assert_called_once()


def test_previous(audio_controller):
    audio_controller.previous()
    audio_controller.list_player.previous.assert_called_once()


def test_increase_volume_when_current_volume_smaller_then_max_volume(audio_controller):
    # setting default volume already during initialization of audio_controller.
    # Calling reset_mock() to reset the call count
    audio_controller.player.audio_set_volume.reset_mock()
    audio_controller.VOLUME["max"] = 100
    audio_controller.player.audio_get_volume.return_value = 50
    audio_controller.increase_volume(10)
    audio_controller.player.audio_set_volume.assert_called_once_with(60)


def test_increase_volume_when_current_volume_equal_max_volume(audio_controller):
    # setting default volume already during initialization of audio_controller.
    # Calling reset_mock() to reset the call count
    audio_controller.player.audio_set_volume.reset_mock()
    audio_controller.VOLUME["max"] = 100
    audio_controller.player.audio_get_volume.return_value = 100
    audio_controller.increase_volume(10)
    audio_controller.player.audio_set_volume.assert_not_called()


def test_decrease_volume_when_current_volume_greater_then_min_volume(audio_controller):
    # setting default volume already during initialization of audio_controller.
    # Calling reset_mock() to reset the call count
    audio_controller.player.audio_set_volume.reset_mock()
    audio_controller.VOLUME["min"] = 0
    audio_controller.player.audio_get_volume.return_value = 50
    audio_controller.decrease_volume(10)
    audio_controller.player.audio_set_volume.assert_called_once_with(40)


def test_decrease_volume_when_current_volume_equal_min_volume(audio_controller):
    # setting default volume already during initialization of audio_controller.
    # Calling reset_mock() to reset the call count
    audio_controller.player.audio_set_volume.reset_mock()
    audio_controller.VOLUME["min"] = 0
    audio_controller.player.audio_get_volume.return_value = 0
    audio_controller.decrease_volume(10)
    audio_controller.player.audio_set_volume.assert_not_called()


def test_get_current_media(audio_controller, caplog):
    expected_logs = ["Currently playing: sample1.mp3"]

    with caplog.at_level(logging.INFO):
        audio_controller.list_player.get_media_player().get_media().get_mrl.return_value = (
            "file:///file/path/to/media/sample1.mp3"
        )
        audio_controller.log_current_media()

    actual_logs = [record.message for record in caplog.records]
    assert actual_logs == expected_logs


def test_logging_current_media_playing(audio_controller, caplog):
    expected_logs = ["No media is currently playing"]

    with caplog.at_level(logging.INFO):
        audio_controller.player.get_media.return_value = None
        audio_controller.log_current_media()

    actual_logs = [record.message for record in caplog.records]
    assert actual_logs == expected_logs


def test_loading_playlist_from_temp_file(audio_controller, tmp_path):
    """Test loading a playlist from a temporary file."""
    temp_file_1 = tmp_path / "temp_song_1.mp3"
    temp_file_2 = tmp_path / "temp_song_2.mp3"
    temp_file_1.touch()
    temp_file_2.touch()
    playlist = [temp_file_1, temp_file_2]
    audio_controller.load_playlist(playlist)

    # Verify that the playlist is loaded correctly
    assert audio_controller.playlist == playlist
    audio_controller.list_player.set_media_list.assert_called_once_with(
        audio_controller.media_list
    )


@pytest.mark.parametrize(
    "file_name, expected",
    [
        ("temp_song.mp3", True),
        ("temp_song.txt", False),
        ("temp_song", False),
    ],
)
def test_is_media_file_valid(tmp_path, file_name, expected):
    temp_file = tmp_path / file_name
    temp_file.touch()
    assert is_media_file_valid(temp_file) == expected


def test_audio_controller_full_sequence(caplog):
    expected_logs = [
        "Playlist loaded with 2 songs",
        "Playback started",
        "Currently playing: music_sample_1.mp3",
        "Song paused",
        "Playback started",
        "Currently playing: music_sample_1.mp3",
        "Next song",
        "Currently playing: music_sample_2.mp3",
        "Previous song",
        "Currently playing: music_sample_1.mp3",
        "Playlist loaded with 2 songs",
        "Playback started",
        "Currently playing: music_sample_3.mp3",
        "Playback stopped",
    ]

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

    with caplog.at_level(logging.INFO):
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

    actual_logs = [record.message for record in caplog.records]
    assert actual_logs == expected_logs


# pytest tests/test_player.py  --cov=src/player --cov-report=html
