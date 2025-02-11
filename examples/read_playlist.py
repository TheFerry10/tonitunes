from dotenv import load_dotenv

from app.cardmanager.db import db_session, init_db
from app.cardmanager.models import Card

load_dotenv(override=True)

init_db()
cards = db_session.query(Card).all()
for card in cards:
    playlist = card.playlist
    if playlist:
        for song in playlist.songs:
            print(song.filename)
