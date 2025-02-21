import os
from pathlib import Path
from typing import Iterable

import pytest

from adapters.repository import SqlAlchemyCardRepositoriy
from adapters.rfid_interface import ResponseHandler, RFIDData, RFIDReadError
from app.cardmanager.models import Card, Playlist, Song
from player.controller import (
    PauseCommand,
    PlayCommand,
    PlayerAction,
    PlayerActionHandler,
    rfid_to_player_action,
)
from rfid.mfrc import AbstractMFRC522, MFRCModule


@pytest.fixture(name="temp_files")
def temp_files_fixture(tmp_path):
    file_1 = tmp_path / "sample1.mp3"
    file_2 = tmp_path / "sample2.mp3"
    file_1.touch()
    file_2.touch()
    return {"file_1": file_1, "file_2": file_2}


@pytest.fixture(name="session_playlist")
def session_playlist_fixture(session, temp_files):
    song_1 = Song(
        title="title_1",
        artist="artist_1",
        album="album_1",
        filename=str(temp_files["file_1"]),
    )
    song_2 = Song(
        title="title_2",
        artist="artist_2",
        album="album_2",
        filename=str(temp_files["file_2"]),
    )
    playlist_ = Playlist(name="test_playlist", songs=[song_1, song_2])
    card_ = Card(name="card", uid="10000000", playlist=playlist_)
    session.add(card_)
    session.commit()
    return session


@pytest.fixture(name="session_real")
def session_real_fixture(session):
    songs = {
        f"song_{idx}": Song(
            title=f"title_{idx}",
            artist=f"artist_{idx}",
            album=f"album_{idx}",
            filename=os.path.abspath(f"tests/resources/music_sample_{idx}.mp3"),
        )
        for idx in [1, 2, 3, 4]
    }
    playlist_1 = Playlist(
        name="test_playlist_1", songs=[songs["song_1"], songs["song_2"]]
    )
    playlist_2 = Playlist(
        name="test_playlist_2", songs=[songs["song_3"], songs["song_4"]]
    )
    card_1 = Card(name="card", uid="10000000", playlist=playlist_1)
    card_2 = Card(name="card", uid="20000000", playlist=playlist_2)
    session.add_all([card_1, card_2])
    session.commit()
    return session


@pytest.mark.parametrize(
    "rfid_data, expected_action",
    [
        (RFIDData("10000000", "test"), PlayerAction("play", "10000000")),
        (RFIDData(), PlayerAction("pause")),
    ],
)
def test_rfid_to_play_action(rfid_data, expected_action):
    action = rfid_to_player_action(rfid_data)
    assert action == expected_action


def test_get_playlist_as_file_paths(session_playlist, temp_files):
    card = session_playlist.query(Card).filter_by(uid="10000000").first()
    playlist = card.get_playlist_as_file_paths()
    assert playlist == [str(temp_files["file_1"]), str(temp_files["file_2"])]


def test_handle_play_action(session_playlist, temp_files):

    expected_play_command = PlayCommand(
        playlist=[
            temp_files["file_1"],
            temp_files["file_2"],
        ]
    )

    repo = SqlAlchemyCardRepositoriy(session_playlist)
    player_action = PlayerAction("play", "10000000")
    player_action_handler = PlayerActionHandler(repo)
    command = player_action_handler.handle(player_action)

    assert command.action == expected_play_command.action
    assert command.playlist == expected_play_command.playlist


def test_handle_pause_action(session_playlist):

    expected_pause_command = PauseCommand()

    repo = SqlAlchemyCardRepositoriy(session_playlist)
    player_action = PlayerAction("pause")
    player_action_handler = PlayerActionHandler(repo)
    command = player_action_handler.handle(player_action)

    assert command.action == expected_pause_command.action


class NoMoreSamples(Exception):
    """No more samples to read"""


class FakeMFRC522(AbstractMFRC522):
    def __init__(self, samples: Iterable):
        self._count = 0
        self._samples = samples

    def read_no_block(self):
        try:
            return next(self._samples)
        except StopIteration:
            raise NoMoreSamples("No more samples to read")


@pytest.fixture(name="reader")
def reader_fixture():
    read_sequence = [
        ("10000000", "sample text"),
        ("10000000", "sample text"),
        ("20000000", "sample text 2"),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        ("20000000", "sample text"),
    ]
    return FakeMFRC522(iter(read_sequence))


@pytest.fixture(name="rfid_module")
def rfid_module_fixture(reader):
    return MFRCModule(reader)


@pytest.fixture(name="repository")
def repository_fixture(session_real):
    return SqlAlchemyCardRepositoriy(session_real)


@pytest.fixture(name="player_action_handler")
def player_action_handler_fixture(repository):
    return PlayerActionHandler(repository)


def test_rfid_player_script(player_action_handler, rfid_module):
    playlist_1 = [
        Path(os.path.abspath(f"tests/resources/music_sample_{idx}.mp3"))
        for idx in [1, 2]
    ]
    playlist_2 = [
        Path(os.path.abspath(f"tests/resources/music_sample_{idx}.mp3"))
        for idx in [3, 4]
    ]
    expected_commands = [
        PlayCommand(playlist_1),
        PlayCommand(playlist_2),
        PauseCommand(),
        PlayCommand(playlist_2),
    ]
    commands = []
    handler = ResponseHandler()
    while True:
        try:
            response = rfid_module.read()
        except RFIDReadError as e:
            assert (
                "Failed to read from RFID module: No more samples to read" == e.message
            )
            break
        handled_response = handler.handle(response)
        if handled_response:
            player_action = rfid_to_player_action(handled_response)
            audio_controller_command = player_action_handler.handle(player_action)
            commands.append(audio_controller_command)
    for c, expected_c in zip(commands, expected_commands):
        assert c.action == expected_c.action
        if isinstance(c, PlayCommand):
            assert c.playlist == expected_c.playlist
