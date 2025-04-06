from app.cardmanager.db import db_session
from app.cardmanager.models import Playlist, Song


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


def test_get_songs_from_playlist(client):
    playlist = Playlist(id=1, name="Playlist 1")
    song1 = Song(id=1, title="Song 1", artist="Artist 1", filename="song1.mp3")
    song2 = Song(id=2, title="Song 2", artist="Artist 2", filename="song2.mp3")
    playlist.songs.extend([song1, song2])
    db_session.add(playlist)
    db_session.commit()

    response = client.get(f"/api/playlists/{playlist.id}/songs")
    assert response.status_code == 200
    assert response.json == [song.to_json() for song in playlist.songs]


def test_get_songs_from_playlist_not_found(client):
    response = client.get("/api/playlists/999/songs")
    assert response.status_code == 404
    assert response.json == {"error": "Playlist not found"}


def test_add_song_to_playlist(client):
    playlist = Playlist(id=1, name="Playlist 1")
    song = Song(id=1, title="Song 1", artist="Artist 1", filename="song1.mp3")
    db_session.add_all([playlist, song])
    db_session.commit()

    response = client.post(f"/api/playlists/{playlist.id}/songs/{song.id}")
    assert response.status_code == 200
    assert song in playlist.songs
    assert response.json == {
        "msg": f"Song {song.artist} - {song.title} added to playlist {playlist.name}"
    }


def test_add_song_to_playlist_not_found(client):
    response = client.post("/api/playlists/999/songs/1")
    assert response.status_code == 404
    assert response.json == {"msg": "Playlist not found"}


def test_delete_song_from_playlist(client):
    playlist = Playlist(id=1, name="Playlist 1")
    song = Song(id=1, title="Song 1", artist="Artist 1", filename="song1.mp3")
    playlist.songs.append(song)
    db_session.add(playlist)
    db_session.commit()

    response = client.delete(f"/api/playlists/{playlist.id}/songs/{song.id}")
    assert response.status_code == 200
    assert song not in playlist.songs
    assert response.json == {
        "msg": (
            f"Song {song.artist} - {song.title} "
            f"removed from playlist {playlist.name}"
        )
    }


def test_delete_song_from_playlist_not_found(client):
    response = client.delete("/api/playlists/999/songs/1")
    assert response.status_code == 404
    assert response.json == {"msg": "Playlist not found"}
