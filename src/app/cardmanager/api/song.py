from flask import jsonify

from ..models import Song
from . import api


@api.route("/songs/artist/<artist>", methods=["GET"])
def get_songs_by_artist(artist: str):
    songs = Song.query.filter_by(artist=artist).all()
    songs_json = [song.to_json() for song in songs]
    return jsonify(songs_json)
