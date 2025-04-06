from app.cardmanager.db import db_session
from app.cardmanager.models import Card


def test_get_cards(client):
    response = client.get("api/card")
    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_post_card(client):
    new_card_data = {"name": "John Doe", "uid": 12345678}
    expected_card = {"name": "John Doe", "uid": 12345678, "playlist_id": None}
    response = client.post("api/card", json=new_card_data)
    assert response.status_code == 200
    card = db_session.query(Card).filter_by(uid=12345678).first()
    assert card.to_json() == expected_card


def test_delete_card(client):
    new_card = Card(name="John Doe", uid=12345678)
    db_session.add(new_card)
    db_session.commit()

    response = client.delete("api/card/12345678")
    assert response.status_code == 200
    card = db_session.query(Card).filter_by(uid=12345678).first()
    assert card is None


def test_update_card_to_song_mapping(client):
    new_card = Card(name="John Doe", uid=12345678)
    db_session.add(new_card)
    db_session.commit()

    response = client.put("api/card/12345678/song/1")
    assert response.status_code == 200
    card = db_session.query(Card).filter_by(uid=12345678).first()
    assert card is not None
    assert card.song_id == 1
