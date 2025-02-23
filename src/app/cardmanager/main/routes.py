import csv
from pathlib import Path
import os
from flask import flash, redirect, render_template, url_for

from ..db import db_session
from ..models import Card, Playlist, Song
from . import main
from .forms import CardPlaylistMappingForm, PlaylistAddSongForm, PlaylistForm


def get_playlist_choices() -> list:
    return [(playlist.id, playlist.name) for playlist in Playlist.query.all()]


@main.route("/", methods=["GET", "POST"])
def index():
    cards = Card.query.all()
    return render_template("index.html", cards=cards)


@main.route("/card/map/<int:card_uid>", methods=["GET", "POST"])
def map_card(card_uid: int):
    form = CardPlaylistMappingForm()
    form.playlist_select.choices = get_playlist_choices()
    if form.validate_on_submit():
        card = Card.query.get(card_uid)
        if card:
            card.playlist_id = form.playlist_select.data
            db_session.add(card)
            db_session.commit()
            flash("Card mapping successful!")
        else:
            flash("Card does not exist")
        return redirect(url_for(".index"))
    return render_template("map-card.html", form=form, card_uid=card_uid)


@main.route("/playlist/edit/<int:playlist_id>", methods=["GET", "POST"])
def edit_playlist(playlist_id: int):
    """
    Edit a playlist by adding songs to it.
    """
    form = PlaylistAddSongForm()
    artists = [song[0] for song in db_session.query(Song.artist).distinct().all()]
    form.artist_select.choices = [(artist, artist) for artist in artists]
    form.title_select.choices = []  # filled dynamically in the template
    playlist = Playlist.query.get(playlist_id)

    if form.validate_on_submit():
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


@main.route("/songs/load", methods=["GET"])
def load_songs():
    home_dir = os.environ.get("TONITUNES_HOME")
    if home_dir:
        file_path_songs = Path(home_dir, "songs/songs.csv")
    else:
        raise ValueError("Environment variable TONITUNES_HOME not defined. Run init script.")
    if file_path_songs.is_file():
        with open(file_path_songs, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            songs = []
            for row in reader:
                if not Song.query.filter_by(
                    title=row["title"], artist=row["artist"]
                ).first():
                    songs.append(Song(**row))
        if songs:
            db_session.add_all(songs)
            db_session.commit()
            flash(f"Loaded {len(songs)} new songs into the database")
        else:
            flash("No new songs to load")
    else:
        flash("No songs file found", category="error")
    return redirect(url_for(".index"))


@main.route("/cards/load", methods=["GET"])
def load_cards():
    home_dir = os.environ.get("TONITUNES_HOME")
    if home_dir:
        file_path_cards = Path(home_dir, "cards/cards.csv")
    else:
        raise ValueError("Environment variable TONITUNES_HOME not defined. Run init script.")
    if file_path_cards.is_file():
        with open(file_path_cards, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            cards = []
            for row in reader:
                if not Card.query.filter_by(uid=row["uid"]).first():
                    cards.append(Card(**row))
        if cards:
            db_session.add_all(cards)
            db_session.commit()
            flash(f"Loaded {len(cards)} cards into the database")
        else:
            flash("No new cards to load")
    else:
        flash("No cards file found", category="error")
    return redirect(url_for(".index"))
