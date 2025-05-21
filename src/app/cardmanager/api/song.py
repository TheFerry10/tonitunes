from flask import jsonify

from ..db import db_session
from ..models import Song
from . import api


@api.route("/songs/artist/<artist>", methods=["GET"])
def get_songs_by_artist(artist: str):
    songs = db_session.query(Song).filter_by(artist=artist).all()
    songs_json = [song.to_json() for song in songs]
    return jsonify(songs_json)


@api.route("/songs/song/<song_id>", methods=["GET"])
def get_song_by_id(song_id: int):
    song = db_session.query(Song).get(song_id)
    if not song:
        return jsonify({"error": "Song not found"}), 404
    return jsonify(song.to_json())


@api.route("/songs", methods=["GET"])
def get_all_songs():
    songs = db_session.query(Song).all()
    songs_json = [song.to_json() for song in songs]
    return jsonify(songs_json)


@api.route("/songs/artist", methods=["GET"])
def get_all_artists():
    artists = db_session.query(Song.artist).distinct().all()
    artists_list = [artist[0] for artist in artists]
    return jsonify({"artists": artists_list})


@api.route("/songs/album", methods=["GET"])
def get_all_albums():
    albums = db_session.query(Song.album).distinct().all()
    albums_list = [album[0] for album in albums]
    return jsonify({"album": albums_list})
