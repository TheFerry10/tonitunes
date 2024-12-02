from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import DeclarativeBase
import csv
import os
from sqlalchemy import ForeignKey, String, Table, Column
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List
from faker import Faker
import random

fake = Faker()

basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = "sqlite:///" + os.path.join(basedir, "test-db.sqlite")
engine = create_engine(DATABASE_URI)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


class Base(DeclarativeBase):
    query = Session.query_property()


association_table = Table(
    "association_table",
    Base.metadata,
    Column("playlist_id", ForeignKey("playlists.id")),
    Column("song_id", ForeignKey("songs.id")),
)


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    artist: Mapped[str]
    album: Mapped[str]
    filename: Mapped[str] = mapped_column(nullable=False, unique=True)
    duration: Mapped[int]
    cards: Mapped[List["Card"]] = relationship("Card", back_populates="song")

    def __repr__(self):
        return f"<Song {self.artist} - {self.title}>"


class Card(Base):
    __tablename__ = "cards"

    uid: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"), nullable=True)
    song: Mapped[Song] = relationship("Song", back_populates="cards")
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.id"), nullable=True)
    playlist: Mapped["Playlist"] = relationship("Playlist", back_populates="cards")

    def __repr__(self):
        return f"<Card {self.uid}>"


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    songs: Mapped[List[Song]] = relationship(secondary=association_table)
    cards: Mapped[List[Card]] = relationship("Card", back_populates="playlist")

    def __repr__(self):
        return f"<Playlist {self.id}>"


def add_songs():
    file_path_songs = "input/out.csv"
    with open(file_path_songs, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        songs = [Song(**row) for row in reader]
    # need to be substituted by a SongRepository
    with Session() as session:
        session.add_all(songs)
        session.commit()


def add_playlists():
    with Session() as session:
        song_list = Song.query.all()
        for _ in range(3):
            sample_songs = random.sample(song_list, random.randint(2, 10))
            playlist = Playlist(name=fake.street_name())
            playlist.songs = sample_songs
            session.add(playlist)
            session.commit()


def add_cards():
    cards = [
        Card(
            uid=fake.random_number(fix_len=True, digits=8),
            name=f"{fake.name()}",
        )
        for _ in range(10)
    ]
    with Session() as session:
        session.add_all(cards)
        session.commit()


def map_playlist_to_card():
    card = Card.query.first()
    card.playlist = Playlist.query.first()
    with Session() as session:
        session.add(card)
        session.commit()


if __name__ == "__main__":
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    add_songs()
    add_playlists()
    add_cards()
    map_playlist_to_card()
    print(Card.query.first().playlist.songs)
