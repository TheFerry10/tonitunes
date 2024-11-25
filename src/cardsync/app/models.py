from sqlalchemy import ForeignKey, String, Table, Column
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .database import Base
from typing import List


association_table = Table(
    "association_table",
    Base.metadata,
    Column("playlist_id", ForeignKey("playlists.id")),
    Column("audio_files_id", ForeignKey("audio_files.id")),
)


class AudioFile(Base):
    __tablename__ = "audio_files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    cards: Mapped[List["Card"]] = relationship(
        "Card", backref="audio_file", lazy="joined"
    )

    def __repr__(self):
        return f"<AudioFile {self.filename}>"


class Card(Base):
    __tablename__ = "cards"

    uid: Mapped[str] = mapped_column(String(30), primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    audio_file_id: Mapped[int] = mapped_column(ForeignKey("audio_files.id"))

    def __repr__(self):
        return f"<Card {self.uid}>"


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    audio_files: Mapped[List[AudioFile]] = relationship(secondary=association_table)
