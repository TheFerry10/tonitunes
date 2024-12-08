import csv
import random

from cardmanager.models import Base, Card, Playlist, Song
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from config import config

config_name = "development"
config = config.get(config_name, "default")
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
session_factory = sessionmaker(bind=engine, autoflush=True)
db_session = scoped_session(session_factory)
Base.query = db_session.query_property()

fake = Faker()


def add_songs(session):
    file_path_songs = "input/out.csv"
    with open(file_path_songs, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        songs = [Song(**row) for row in reader]
    session.add_all(songs)
    session.commit()


def add_playlists(session):
    song_list = Song.query.all()
    sample_songs = random.sample(song_list, random.randint(2, 10))
    for _ in range(3):
        playlist = Playlist(name=fake.street_name())

        playlist.songs = sample_songs

        session.add(playlist)
    session.commit()


def add_cards(session):
    cards = [
        Card(
            uid=fake.random_number(fix_len=True, digits=8),
            name=f"{fake.name()}",
        )
        for _ in range(10)
    ]
    session.add_all(cards)
    session.commit()


def map_playlist_to_card(session):

    card = Card.query.first()
    card.playlist = Playlist.query.first()
    session.add(card)
    session.commit()


if __name__ == "__main__":
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with db_session() as s:
        add_songs(s)
        add_playlists(s)
        add_cards(s)
        map_playlist_to_card(s)
