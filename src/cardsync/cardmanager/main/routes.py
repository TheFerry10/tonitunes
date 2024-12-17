from flask import flash, redirect, render_template, url_for

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
    form = CardPlaylistMappingForm()
    form.card_select.choices = get_card_choices()
    form.playlist_select.choices = get_playlist_choices()
    if form.validate_on_submit():
        card = Card.query.get(form.card_select.data)
        card.playlist_id = form.playlist_select.data
        db_session.add(card)
        db_session.commit()
        flash("Card mapping successful!")
        return redirect(url_for(".index"))
    cards = Card.query.all()
    return render_template("index.html", form=form, cards=cards)


@main.route("/playlist/edit/<int:playlist_id>", methods=["GET", "POST"])
def edit_playlist(playlist_id: int):
    form = PlaylistAddSongForm()
    form.song_select.choices = [
        (s.id, f"{s.artist} - {s.title}") for s in Song.query.all()
    ]
    playlist = Playlist.query.get(playlist_id)

    if form.validate_on_submit():
        song_id = form.song_select.data
        song_to_add = Song.query.get(song_id)
        playlist.songs.append(song_to_add)
        db_session.add(playlist)
        db_session.commit()
        flash("Song added to playlist successfully!")
        return redirect(url_for(".edit_playlist", playlist_id=playlist_id))

    return render_template("playlist-edit.html", form=form, playlist=playlist)


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
