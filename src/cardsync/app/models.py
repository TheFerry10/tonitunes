from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base


class Card(Base):
    __tablename__ = "cards"
    uid = Column(String(64), primary_key=True)
    name = Column(String(64))
    audio_file_id = Column(Integer, ForeignKey("audio_files.id"))

    def __repr__(self):
        return f"<Card {self.uid}>"


class AudioFile(Base):
    __tablename__ = "audio_files"
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(64), unique=True, nullable=False)
    cards = relationship("Card", backref="audio_file", lazy="joined")

    def __repr__(self):
        return f"<AudioFile {self.filename}>"
