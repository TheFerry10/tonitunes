import csv

from ..cardmanager.db import db_session
from ..cardmanager.main.routes import (
    filter_new_cards,
    is_card_in_db,
    load_model_instances_from_csv,
)
from ..cardmanager.models import Card, Playlist


def test_index(client):
    """
    Test the index route.
    """

    response = client.get("/")
    assert response.status_code == 200
    assert b"Cards" in response.data

    # should contain "Card Mappings"


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
