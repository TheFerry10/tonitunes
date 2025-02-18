from player.controller import (
    rfid_to_player_action,
    PlayerAction,
    handle_play_action,
    PlayerActionHandler,
)
from app.cardmanager.models import Card, Song, Playlist
from adapters.rfid_interface import RFIDData

import pytest


@pytest.fixture(name="session_playlist")
def session_playlist_fixture(session):
    song_1 = Song(
        title="title_1",
        artist="artist_1",
        album="album_1",
        filename="/file/path/sample1.mp3",
    )
    song_2 = Song(
        title="title_2",
        artist="artist_2",
        album="album_2",
        filename="/file/path/sample2.mp3",
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


def test_get_playlist_as_file_paths(session_playlist):
    card = session_playlist.query(Card).filter_by(uid="10000000").first()
    playlist = card.get_playlist_as_file_paths()
    assert playlist == ["/file/path/sample1.mp3", "/file/path/sample2.mp3"]
