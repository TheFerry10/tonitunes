from pathlib import Path
from player.controller import (
    rfid_to_player_action,
    PlayerAction,
    PlayCommand,
    PauseCommand,
    PlayerActionHandler,
)
from adapters.repository import SqlAlchemyCardRepositoriy
from app.cardmanager.models import Card, Song, Playlist
from adapters.rfid_interface import RFIDData

import pytest


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
