import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

db_session = scoped_session(sessionmaker())


def init_db(database_uri):
    """Initialize the database schema (creates tables)."""
    engine = create_engine(database_uri, echo=False)
    db_session.configure(bind=engine)
    from .models import Base, Card, Playlist, Song  # noqa: F401

    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=engine)
    logging.info("Database initialized")
    logging.info(f"Database URI: {database_uri}")


def drop_db(database_uri):
    """Drop all tables in the database."""
    engine = create_engine(database_uri, echo=False)
    from .models import Base

    Base.metadata.drop_all(bind=engine)
    logging.info("Database tables dropped")
