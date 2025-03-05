from typing import Dict, List, Union

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


association_table = Table(
    "association_table",
    Base.metadata,
    Column("playlist_id", ForeignKey("playlists.id")),
    Column("song_id", ForeignKey("songs.id")),
)


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    artist: Mapped[str] = mapped_column(nullable=False)
    album: Mapped[str] = mapped_column(nullable=True)
    filename: Mapped[str] = mapped_column(nullable=False, unique=True)
    duration: Mapped[int] = mapped_column(nullable=True)
    cards: Mapped[list["Card"]] = relationship("Card", back_populates="song")

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
    name: Mapped[str] = mapped_column(nullable=False)
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

    def get_playlist_as_file_paths(self) -> List[str]:
        if self.playlist:
            return [song.filename for song in self.playlist.songs]


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    songs: Mapped[List[Song]] = relationship(secondary=association_table)
    cards: Mapped[List[Card]] = relationship("Card", back_populates="playlist")

    def from_json(
        self, json_playlist: Dict[str, Union[str, List[Dict[str, Union[str, str]]]]]
    ):
        raise NotImplementedError()

    def to_json(self):
        playlist_json = {
            "id": self.id,
            "name": self.name,
            "songs": [song.to_json() for song in self.songs],
        }
        return playlist_json

    def __repr__(self):
        return f"<Playlist {self.id}>"
