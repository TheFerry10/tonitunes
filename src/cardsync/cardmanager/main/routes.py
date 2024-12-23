from flask import flash, redirect, render_template, url_for, jsonify, request

from ..db import db_session
from ..models import Card, Playlist, Song
from . import main
from .forms import CardPlaylistMappingForm, PlaylistAddSongForm, PlaylistForm


def get_card_choices() -> list:
    return [
        (card.uid, " - ".join([str(card.uid), card.name])) for card in Card.query.all()
    ]


def get_playlist_choices() -> list:
    return [(playlist.id, playlist.name) for playlist in Playlist.query.all()]


@main.route("/", methods=["GET", "POST"])
def index():
    cards = Card.query.all()
    return render_template("index.html", cards=cards)


@main.route("/card/add/<int:card_uid>", methods=["GET", "POST"])
def add_card(card_uid: int):
    form = CardPlaylistMappingForm()
    form.playlist_select.choices = get_playlist_choices()
    if form.validate_on_submit():
        card = Card.query.get(card_uid)
        card.playlist_id = form.playlist_select.data
        db_session.add(card)
        db_session.commit()
        flash("Card mapping successful!")
        return redirect(url_for(".index"))
    return render_template("add-card.html", form=form, card_uid=card_uid)


@main.route("/playlist/edit/<int:playlist_id>", methods=["GET", "POST"])
def edit_playlist(playlist_id: int):
    """
    Edit a playlist by adding songs to it.
    """
    form = PlaylistAddSongForm()
    artists = [song[0] for song in db_session.query(Song.artist).distinct().all()]
    form.artist_select.choices = [(artist, artist) for artist in artists]
    form.title_select.choices = []
    playlist = Playlist.query.get(playlist_id)

    if request.method == "POST":
        form.validate()
        print(form.errors)
        song_id = form.title_select.data
        song_to_add = Song.query.get(song_id)
        playlist.songs.append(song_to_add)
        db_session.add(playlist)
        db_session.commit()
        flash("Song added to playlist successfully!")
        return redirect(url_for(".edit_playlist", playlist_id=playlist_id))

    return render_template(
        "playlist-edit.html", form=form, playlist=playlist, artists=artists
    )


@main.route("/playlist/manage", methods=["GET", "POST"])
def manage_playlists():
    form = PlaylistForm()
    if form.validate_on_submit():
        new_playlist = Playlist(name=form.name.data)
        db_session.add(new_playlist)
        db_session.commit()
        flash("Playlist created successfully!")
        return redirect(url_for(".manage_playlists"))
    playlists = Playlist.query.all()
    return render_template("playlists-manage.html", form=form, playlists=playlists)


@main.route("/playlists/delete/<int:playlist_id>", methods=["POST"])
def delete_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    if playlist:
        db_session.delete(playlist)
        db_session.commit()
        flash("Playlist deleted successfully!")
    else:
        flash("Playlist not found!")
    return redirect(url_for(".manage_playlists"))


@main.route("/playlists/<int:playlist_id>/song/delete/<int:song_id>", methods=["POST"])
def remove_song_from_playlist(playlist_id, song_id):
    playlist = Playlist.query.get(playlist_id)
    if playlist:
        song = Song.query.get(song_id)
        if song in playlist.songs:
            playlist.songs.remove(song)
            db_session.add(playlist)
            db_session.commit()
            flash("Song deleted successfully!")
    else:
        flash("Song not found!")
    return redirect(url_for(".edit_playlist", playlist_id=playlist_id))


@main.route("/songs/artist/<artist>", methods=["GET"])
def get_songs_by_artist(artist: str):
    songs = Song.query.filter_by(artist=artist).all()
    songs_json = [song.to_json() for song in songs]
    return jsonify(songs_json)
