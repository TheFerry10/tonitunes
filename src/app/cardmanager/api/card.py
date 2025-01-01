from flask import jsonify, request

from ..db import db_session
from ..models import Card
from . import api


@api.route("/card", methods=["GET"])
def get_cards():
    cards = Card.query.all()
    r = [card.to_json() for card in cards]
    return jsonify(r)


@api.route("/card", methods=["POST"])
def new_card():
    card = Card.from_json(request.json)
    existing_card = Card.query.filter_by(uid=card.uid).first()
    if existing_card:
        existing_card.name = card.name
        db_session.add(existing_card)
    else:
        db_session.add(card)
    db_session.commit()
    return jsonify(card.to_json())


@api.route("/card/<int:uid>", methods=["DELETE"])
def delete_card(uid: int):
    card = Card.query.filter_by(uid=uid).first()
    if card:
        db_session.delete(card)
        db_session.commit()
        return jsonify(card.to_json())
    else:
        return jsonify({"msg": f"Card with uid {uid} does not exist"})


@api.route("/card/<int:uid>/song/<int:song_id>", methods=["PUT"])
def update_card_to_song_mapping(uid: int, song_id: int):
    card = Card.query.filter_by(uid=uid).first()
    if card:
        card.song_id = song_id
        db_session.add(card)
        db_session.commit()
        return jsonify(card.to_json())
    else:
        return jsonify({"msg": f"Card with uid {uid} does not exist"})
