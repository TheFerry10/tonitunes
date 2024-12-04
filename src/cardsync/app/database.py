from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase
import os
from config import config

flask_config = os.getenv("FLASK_CONFIG", "default")
DATABASE_URI = config[flask_config].SQLALCHEMY_DATABASE_URI


engine = create_engine(DATABASE_URI, echo=False)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


class Base(DeclarativeBase):
    query = db_session.query_property()


def init_db():

    from .models import Card, Song, Playlist

    Base.metadata.create_all(bind=engine)
