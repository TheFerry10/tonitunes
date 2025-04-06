import pytest

from app.cardmanager import create_app
from app.cardmanager.db import db_session, drop_db, init_db


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        yield app
        db_session.remove()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db(app):
    """Setup and teardown the database for each test."""
    print(app.config)
    init_db(app.config["DATABASE_URI"])
    yield
    db_session.remove()
    drop_db(app.config["DATABASE_URI"])
