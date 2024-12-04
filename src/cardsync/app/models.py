from sqlalchemy import ForeignKey, String, Table, Column
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .database import Base
from typing import List, Dict, Union
from dataclasses import asdict


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

    def to_json(self):
        song_json = {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "filename": self.filename,
            "duration": self.duration,
        }
        return song_json


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

    @staticmethod
    def from_json(json_card: Dict[str, Union[str, str]]):
        uid = json_card.get("uid")
        if uid:
            uid = int(uid)
        else:
            raise ValueError("uid is is empty")
        name = json_card.get("name")
        return Card(uid=uid, name=name)

    def to_json(self):
        card_json = {"uid": self.uid, "name": self.name}
        return card_json


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    songs: Mapped[List[Song]] = relationship(secondary=association_table)
    cards: Mapped[List[Card]] = relationship("Card", back_populates="playlist")

    def __repr__(self):
        return f"<Playlist {self.id}>"
