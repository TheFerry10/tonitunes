from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import DeclarativeBase
import os
from sqlalchemy import ForeignKey, String, Table, Column
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List
from faker import Faker

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


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    artist: Mapped[str]
    album: Mapped[str]
    filename: Mapped[str] = mapped_column(nullable=False, unique=True)
    duration: Mapped[int]


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

    def __repr__(self):
        return f"<Playlist {self.id}>"


def insert_filenames():
    with open("media_archive.txt", "r", encoding="utf-8", newline="\n") as f:
        lines = [line.strip() for line in f]
    print(lines)
    audio_files = [AudioFile(filename=filename) for filename in lines]

    session = Session()
    session.add_all(audio_files)
    session.commit()
    session.close()


def read_filenames():
    session = Session()
    return [row[0] for row in session.query(AudioFile.filename).all()]


def read_cards():
    session = Session()
    return (
        session.query(Card.uid, Card.name, AudioFile.filename)
        .outerjoin(AudioFile)
        .all()
    )


def add_filenames():
    with Session() as session:
        audio_files = [AudioFile(filename=fake.name()) for _ in range(10)]
        playlist = Playlist(name="my playlist")
        playlist.audio_files.append(audio_files[0])
        playlist.audio_files.append(audio_files[1])
        session.add_all(audio_files)
        session.add(playlist)
        session.commit()


def add_songs():
    import csv

    with open("input/out.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        songs = [Song(**row) for row in reader]
    with Session() as session:
        session.add_all(songs)
        session.commit()

    # add_filenames()
    # playlist = Playlist.query.first()
    # print(playlist.audio_files)
    # with Session() as session:
    #     a = AudioFile(filename=fake.name())
    #     p = Playlist(name="new")
    #     p.audio_files = AudioFile.query.all()
    #     session.add(p)
    #     session.commit()


if __name__ == "__main__":
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    add_songs()

# read all cards
#
