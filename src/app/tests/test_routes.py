import csv

from ..cardmanager.db import db_session
from ..cardmanager.main.routes import (
    filter_new_cards,
    filter_new_songs,
    is_card_in_db,
    load_model_instances_from_csv,
)
from ..cardmanager.models import Card, Playlist, Song


def test_index(client):
    """
    Test the index route.
    """

    response = client.get("/")
    assert response.status_code == 200
    assert b"Card Mappings" in response.data


def test_edit_playlist(client):
    playlist = Playlist(id=1, name="Test Playlist")
    db_session.add(playlist)
    db_session.commit()

    response = client.get("/playlist/edit/1")
    assert response.status_code == 200
    assert b"Add songs" in response.data


def test_manage_playlists(client):
    response = client.get("/playlist/manage")
    assert response.status_code == 200
    assert b"Create a New Playlist" in response.data


def test_load_model_from_csv(tmp_path):
    """
    Test the load_model_from_csv function.
    """
    csv_file = tmp_path / "test_cards.csv"
    csv_data = [
        {"uid": "1", "name": "Card 1"},
        {"uid": "2", "name": "Card 2"},
    ]
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["uid", "name"])
        writer.writeheader()
        writer.writerows(csv_data)

    cards = load_model_instances_from_csv(Card, csv_file)

    assert len(cards) == 2
    assert cards[0].uid == "1"
    assert cards[0].name == "Card 1"
    assert cards[1].uid == "2"
    assert cards[1].name == "Card 2"


def test_return_true_when_card_in_db():
    existing_card = Card(uid="1", name="Existing Card")
    db_session.add(existing_card)
    db_session.commit()

    assert is_card_in_db(existing_card, db_session)


def test_return_false_when_card_not_in_db():
    new_card = Card(uid="2", name="New Card")
    assert not is_card_in_db(new_card, db_session)


def test_retrieve_nonexistent_cards():
    """
    Test the get_cards_that_do_not_exist_in_db function.
    """

    existing_card_1 = Card(uid="1", name="Existing Card 1")
    existing_card_2 = Card(uid="2", name="Existing Card 2")
    db_session.add_all([existing_card_1, existing_card_2])
    db_session.commit()

    card_1 = Card(uid="1", name="Existing Card 1")
    card_2 = Card(uid="2", name="Existing Card 2")
    card_3 = Card(uid="3", name="New Card 3")
    card_4 = Card(uid="4", name="New Card 4")
    cards = [card_1, card_2, card_3, card_4]
    expected_cards = [card_3, card_4]

    new_cards = filter_new_cards(cards, db_session)

    assert new_cards == expected_cards


def test_retrieve_nonexistent_songs():
    """
    Test the get_songs_that_do_not_exist_in_db function.
    """

    existing_song = Song(
        title="dummy title 1",
        artist="dummy artist 1",
        album="dummy album 1",
        filename="dummy1.mp3",
        duration=10000,
    )
    new_song_1 = Song(
        title="dummy title 2",
        artist="dummy artist 2",
        album="dummy album 2",
        filename="dummy2.mp3",
        duration=20000,
    )
    new_song_2 = Song(
        title="dummy title 2",
        artist="dummy artist 2",
        album="dummy album 2",
        filename="dummy2.mp3",
        duration=20000,
    )
    db_session.add_all([existing_song])
    db_session.commit()

    songs = [existing_song, new_song_1, new_song_2]
    expected_songs = [new_song_1, new_song_2]

    new_songs = filter_new_songs(songs, db_session)

    assert new_songs == expected_songs


def test_load_cards(client):

    expected_cards = [
        Card(uid=12411690, name="Blue Card"),
        Card(uid=34976129, name="Red Card"),
        Card(uid=49353438, name="Yellow Card"),
        Card(uid=55852923, name="Black Card"),
        Card(uid=60337619, name="Green Card"),
    ]

    response = client.get("/cards/load")
    assert response.status_code == 302
    cards = db_session.query(Card.uid, Card.name).all()
    assert cards == [(card.uid, card.name) for card in expected_cards]


def test_load_songs(client):
    expected_songs = [
        Song(
            title="dummy title 1",
            artist="dummy artist 1",
            album="dummy album 1",
            filename="dummy1.mp3",
            duration=10000,
        ),
        Song(
            title="dummy title 2",
            artist="dummy artist 2",
            album="dummy album 2",
            filename="dummy2.mp3",
            duration=20000,
        ),
    ]

    response = client.get("/songs/load")
    assert response.status_code == 302
    songs = db_session.query(Song.title, Song.artist).all()
    assert songs == [(song.title, song.artist) for song in expected_songs]
