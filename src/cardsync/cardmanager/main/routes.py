from flask import flash, redirect, render_template, url_for

from ..db import db_session
from ..models import Card, Playlist, Song
from . import main
from .forms import FileMappingForm, PlaylistAddSongForm, PlaylistForm


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


@main.route("/playlist/edit", methods=["GET", "POST"])
def edit_playlist():
    table_header = ("Playlist Name", "Artist", "Title", "Action")
    playlists = Playlist.query.all()
    form = PlaylistAddSongForm()
    form.playlist_identifier.choices = [(p.id, p.name) for p in playlists]
    form.song_selection.choices = [
        (s.id, f"{s.artist} - {s.title}") for s in Song.query.all()
    ]

    if form.validate_on_submit():
        playlist_id = form.playlist_identifier.data
        song_id = form.song_selection.data
        song_to_add = Song.query.get(song_id)
        playlist = Playlist.query.get(playlist_id)
        playlist.songs.append(song_to_add)
        db_session.add(playlist)
        db_session.commit()
        flash("Song added to playlist successfully!")
        return redirect(url_for(".edit_playlist"))

    return render_template(
        "playlist-edit.html", form=form, table_header=table_header, playlists=playlists
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
    return redirect(url_for(".edit_playlist"))
