from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import AudioFile, Card

DATABASE_URL = "sqlite:///data.sqlite"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)


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


if __name__ == "__main__":
    result = read_filenames()
    print(result)
