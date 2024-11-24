from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


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


def init_engine_and_session(database_uri="sqlite:///test.db"):
    engine = create_engine(database_uri)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session
