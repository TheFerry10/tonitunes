from flask import flash, redirect, render_template, url_for, jsonify, request

from ..database import db_session
from ..models import Song, Card, Playlist
from . import main
from .forms import FileMappingForm


def get_cards():
    return (
        db_session.query(Card.uid, Card.name, Song.artist, Song.title)
        .outerjoin(Song)
        .all()
    )


def get_card_identifier_options() -> list:
    return [
        (card.uid, " - ".join([str(card.uid), card.name])) for card in Card.query.all()
    ]


def get_filenames():
    return [(audio_file.id, audio_file.filename) for audio_file in Song.query.all()]


@main.route("/", methods=["GET", "POST"])
def index():
    table_header = ("Card Id", "Card Name", "Artist", "Title")
    table_data = get_cards()
    form = FileMappingForm()
    card_options = get_card_identifier_options()
    form.card_identifier.choices = card_options
    form.file_name.choices = get_filenames()
    if form.validate_on_submit():
        card = Card.query.filter_by(uid=form.card_identifier.data).first()
        card.song_id = form.file_name.data
        db_session.add(card)
        db_session.commit()
        flash("File mapping successfully updated!")
        return redirect(url_for(".index"))
    return render_template(
        "index.html",
        form=form,
        table_header=table_header,
        table_data=table_data,
    )


@main.route("/cards/", methods=["POST"])
def new_card():
    card = Card.from_json(request.json)
    existing_card = Card.query.filter_by(uid=card.uid).first()
    if existing_card:
        existing_card.name = card.name
        db_session.add(existing_card)
    else:
        db_session.add(card)
    db_session.commit()
    return jsonify(card.to_json())


@main.route("/cards/<int:uid>", methods=["DELETE"])
def delete_card(uid: int):
    card = Card.query.filter_by(uid=uid).first()
    if card:
        db_session.delete(card)
        db_session.commit()
        return jsonify(card.to_json())
    else:
        return jsonify({"msg": f"Card with uid {uid} does not exists"})


# "/playlists/<int:id>/songs" POST add new song to playlist
# "/playlists/<int:id>/songs" GET return all songs in playlist
# "/playlists/<int:id>/songs/<int:id>" DELETE remove song from playlist


@main.route("/playlists/<int:id>/songs/", methods=["GET"])
def get_songs_from_playlist(id: int):
    playlist = Playlist.query.filter_by(id=id).first()
    if playlist:
        songs_ = [song.to_json() for song in playlist.songs]
        return jsonify(songs_)


@main.route("/playlists/<int:playlist_id>/songs/<int:song_id>", methods=["POST"])
def add_song_to_playlist(playlist_id: int, song_id: int):
    playlist = Playlist.query.filter_by(id=playlist_id).first()
    if playlist:
        song = Song.query.filter_by(id=song_id).first()
        playlist.songs.append(song)
        db_session.add(playlist)
        db_session.commit()
        return jsonify(
            {
                "msg": f"Song {song.artist} - {song.title} added to playlist {playlist.name}"
            }
        )
