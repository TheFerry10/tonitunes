import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.cardmanager.models import Base


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    yield session

    session.close()
