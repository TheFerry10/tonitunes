from ..cardmanager.db import db_session
from ..cardmanager.models import Song


def test_get_songs_by_artist(client):
    songs = [
        Song(id=1, title="Song 1", artist="Artist 1", filename="song1.mp3"),
        Song(id=2, title="Song 2", artist="Artist 1", filename="song2.mp3"),
    ]
    db_session.add_all(songs)
    db_session.commit()

    response = client.get("api/songs/artist/Artist 1")
    assert response.status_code == 200
    assert response.json == [song.to_json() for song in songs]
