import os

from dotenv import load_dotenv

from app.cardmanager.db import db_session, init_db
from app.cardmanager.models import Card

load_dotenv(override=True)

user = os.getenv("USER")
database_path = os.path.abspath(f"/home/{user}/tmp/default.db")
DATABASE_URI = os.getenv("DATABASE_URI", f"sqlite:///{database_path}")
init_db(database_uri=DATABASE_URI)
cards = db_session.query(Card).all()
for card in cards:
    playlist = card.playlist
    if playlist:
        for song in playlist.songs:
            print(song.filename)
