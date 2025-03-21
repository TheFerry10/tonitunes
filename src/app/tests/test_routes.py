from ..cardmanager.db import db_session
from ..cardmanager.models import Playlist


def test_index(client):
    """
    Test the index route.
    """

    response = client.get("/")
    assert response.status_code == 200
    assert b"Cards" in response.data

    # should contain "Card Mappings"


def test_edit_playlist(client):
    playlist = Playlist(id=1, name="Test Playlist")
    db_session.add(playlist)
    db_session.commit()

    response = client.get("/playlist/edit/1")
    assert response.status_code == 200
    assert b"Add songs" in response.data


def test_manage_playlists(client):
    response = client.get("/playlist/manage")
    assert response.status_code == 200
    assert b"Create a New Playlist" in response.data
