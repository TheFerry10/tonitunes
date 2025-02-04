import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .config import config

flask_config = os.getenv("FLASK_CONFIG", "default")
DATABASE_URI = config[flask_config].SQLALCHEMY_DATABASE_URI


engine = create_engine(DATABASE_URI, echo=False)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def init_db():
    """Initialize the database schema (creates tables)."""
    from .models import Base, Card, Playlist, Song  # noqa: F401

    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=engine)
    print(DATABASE_URI)


def bind_query_property():
    """Bind query property to the database session."""
    from .models import Base

    Base.query = db_session.query_property()
