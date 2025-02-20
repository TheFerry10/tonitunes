from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_session = scoped_session(sessionmaker())


def init_db(database_uri):
    """Initialize the database schema (creates tables)."""
    engine = create_engine(database_uri, echo=True)
    db_session.configure(bind=engine)
    from .models import Base, Card, Playlist, Song  # noqa: F401

    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=engine)
    print(database_uri)


def bind_query_property(database_uri):
    """Bind query property to the database session."""
    engine = create_engine(database_uri, echo=False)
    db_session.configure(bind=engine)
    from .models import Base

    Base.query = db_session.query_property()
