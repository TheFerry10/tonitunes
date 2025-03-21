from flask import jsonify, request

from ..db import db_session
from ..models import Playlist, Song
from . import api


@api.route("/playlists/<int:playlist_id>/songs", methods=["GET"])
def get_songs_from_playlist(playlist_id: int):
    playlist = db_session.get(Playlist, playlist_id)
    if playlist:
        songs_ = [song.to_json() for song in playlist.songs]
        return jsonify(songs_)


@api.route("/playlists", methods=["GET"])
def get_playlists():
    playlists = db_session.query(Playlist).all()
    playlists_ = [playlist.to_json() for playlist in playlists]
    return jsonify(playlists_)


@api.route("/playlists/<int:playlist_id>", methods=["DELETE"])
def delete_playlist(playlist_id: int):
    playlist = db_session.get(Playlist, playlist_id)
    if playlist:
        db_session.delete(playlist)
        db_session.commit()
        return jsonify(playlist.to_json())
    else:
        return jsonify({"msg": f"Playlist with id {playlist_id} does not exist"})


@api.route("/playlists", methods=["POST"])
def create_playlist():
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
    playlist = Playlist.query.filter_by(id=playlist_id).first()
    if playlist:
        song = Song.query.filter_by(id=song_id).first()
        if song in playlist.songs:
            playlist.songs.remove(song)
            db_session.add(playlist)
            db_session.commit()
            return jsonify(
                {
                    "msg": f"Song {song.artist} - {song.title} removed from playlist {playlist.name}"  # noqa: E501
                }
            )
        else:
            return jsonify({"msg": "Song not found in playlist"}), 404
    return jsonify({"msg": "Playlist not found"}), 404


@api.route("/playlists/<int:playlist_id>/songs/<int:song_id>", methods=["POST"])
def add_song_to_playlist(playlist_id: int, song_id: int):
    playlist = Playlist.query.filter_by(id=playlist_id).first()
    if playlist:
        song = Song.query.filter_by(id=song_id).first()
        playlist.songs.append(song)
        db_session.add(playlist)
        db_session.commit()
        return jsonify(
            {
                "msg": f"Song {song.artist} - {song.title} added to playlist {playlist.name}"  # noqa: E501
            }
        )
