from ..cardmanager.db import db_session
from ..cardmanager.models import Playlist


def test_get_playlists(client):
    playlists = [
        Playlist(id=1, name="Playlist 1"),
        Playlist(id=2, name="Playlist 2"),
    ]
    db_session.add_all(playlists)
    db_session.commit()

    response = client.get("/api/playlists")
    assert response.status_code == 200
    assert response.json == [playlist.to_json() for playlist in playlists]


def test_post_playlist(client):
    new_playlist_data = {"name": "New Playlist"}
    response = client.post("/api/playlists", json=new_playlist_data)
    assert response.status_code == 201
    playlist = db_session.query(Playlist).filter_by(name="New Playlist").first()
    assert playlist is not None
    assert playlist.to_json() == {
        "id": playlist.id,
        "name": "New Playlist",
        "songs": [],
    }


def test_delete_playlist(client):
    playlist = Playlist(id=1, name="Playlist to Delete")
    db_session.add(playlist)
    db_session.commit()

    response = client.delete(f"/api/playlists/{playlist.id}")
    assert response.status_code == 200
    deleted_playlist = db_session.query(Playlist).filter_by(id=playlist.id).first()
    assert deleted_playlist is None
