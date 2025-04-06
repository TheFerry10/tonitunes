from flask import jsonify, request

from ..db import db_session
from ..models import Playlist, Song
from . import api


@api.route("/playlists/<int:playlist_id>/songs", methods=["GET"])
def get_songs_from_playlist(playlist_id: int):
    """
    Get all songs from a specific playlist.

    Args:
        playlist_id (int): The ID of the playlist.

    Returns:
        Response: JSON response containing the list of songs or an error message.
    """
    playlist = db_session.get(Playlist, playlist_id)
    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404
    songs_ = [song.to_json() for song in playlist.songs]
    return jsonify(songs_)


@api.route("/playlists", methods=["GET"])
def get_playlists():
    """
    Get all playlists.

    Returns:
        Response: JSON response containing the list of playlists.
    """
    playlists = db_session.query(Playlist).all()
    playlists_ = [playlist.to_json() for playlist in playlists]
    return jsonify(playlists_)


@api.route("/playlists/<int:playlist_id>", methods=["DELETE"])
def delete_playlist(playlist_id: int):
    """
    Delete a specific playlist.

    Args:
        playlist_id (int): The ID of the playlist to delete.

    Returns:
        Response: JSON response containing the deleted playlist or an error message.
    """
    playlist = db_session.get(Playlist, playlist_id)
    if not playlist:
        return jsonify({"msg": f"Playlist with id {playlist_id} does not exist"})
    db_session.delete(playlist)
    db_session.commit()
    return jsonify(playlist.to_json())


@api.route("/playlists", methods=["POST"])
def create_playlist():
    """
    Create a new playlist.

    Returns:
        Response: JSON response containing the created playlist or an error message.
    """
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"msg": "Playlist name is required"}), 400

    new_playlist = Playlist(name=name)
    db_session.add(new_playlist)
    db_session.commit()

    return jsonify(new_playlist.to_json()), 201


@api.route("/playlists/<int:playlist_id>/songs/<int:song_id>", methods=["DELETE"])
def delete_song_from_playlist(playlist_id: int, song_id: int):
    """
    Remove a song from a specific playlist.

    Args:
        playlist_id (int): The ID of the playlist.
        song_id (int): The ID of the song to remove.

    Returns:
        Response: JSON response confirming the removal or an error message.
    """
    playlist = Playlist.query.filter_by(id=playlist_id).first()
    if not playlist:
        return jsonify({"msg": "Playlist not found"}), 404

    song = Song.query.filter_by(id=song_id).first()

    if song not in playlist.songs:
        return jsonify({"msg": "Song not found in playlist"}), 404

    playlist.songs.remove(song)
    db_session.add(playlist)
    db_session.commit()
    return jsonify(
        {
            "msg": f"Song {song.artist} - {song.title} removed from playlist {playlist.name}"  # noqa: E501
        }
    )


@api.route("/playlists/<int:playlist_id>/songs/<int:song_id>", methods=["POST"])
def add_song_to_playlist(playlist_id: int, song_id: int):
    """
    Add a song to a specific playlist.

    Args:
        playlist_id (int): The ID of the playlist.
        song_id (int): The ID of the song to add.

    Returns:
        Response: JSON response confirming the addition or an error message.
    """
    playlist = Playlist.query.filter_by(id=playlist_id).first()
    if not playlist:
        return jsonify({"msg": "Playlist not found"}), 404

    song = Song.query.filter_by(id=song_id).first()
    playlist.songs.append(song)
    db_session.add(playlist)
    db_session.commit()
    return jsonify(
        {
            "msg": f"Song {song.artist} - {song.title} added to playlist {playlist.name}"  # noqa: E501
        }
    )
