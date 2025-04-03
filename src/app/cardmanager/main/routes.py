import csv
from pathlib import Path
from typing import List

from flask import current_app, flash, redirect, render_template, url_for
from sqlalchemy.orm import Session

from ..db import db_session
from ..models import Base, Card, Playlist, Song
from . import main
from .forms import CardPlaylistMappingForm, PlaylistAddSongForm, PlaylistForm

app = current_app


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
    playlist = db_session.get(Playlist, playlist_id)

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
    file_path = Path(app.config["TONITUNES_SONGS_DIR"], "songs.csv")
    if not file_path.is_file():
        flash("No songs file found", category="error")
        return redirect(url_for(".index"))

    songs = load_model_instances_from_csv(Song, file_path)
    new_songs = filter_new_songs(songs, db_session)
    if songs:
        db_session.add_all(new_songs)
        db_session.commit()
        flash(f"Loaded {len(new_songs)} new songs into the database")
    else:
        flash("No new songs to load", category="info")
    return redirect(url_for(".index"))


@main.route("/cards/load", methods=["GET"])
def load_cards():
    file_path = Path(app.config["TONITUNES_CARDS_DIR"], "cards.csv")
    if not file_path.is_file():
        flash("No cards file found", category="error")
        return redirect(url_for(".index"))

    cards = load_model_instances_from_csv(Card, file_path)
    new_cards = filter_new_cards(cards, db_session)
    if new_cards:
        db_session.add_all(new_cards)
        db_session.commit()
        flash(f"Loaded {len(new_cards)} cards into the database")
    else:
        flash("No new cards to load", category="info")
    return redirect(url_for(".index"))


def load_model_instances_from_csv(model: Base, file_path: Path) -> list[Base]:
    with open(file_path, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        return [model(**row) for row in reader]


def is_card_in_db(card: Card, session: Session) -> bool:
    return session.get(Card, card.uid) is not None


def filter_new_cards(cards: List[Card], session: Session) -> List[Card]:
    return [card for card in cards if session.get(Card, card.uid) is None]


def filter_new_songs(songs: List[Song], session: Session) -> List[Song]:
    return [
        song
        for song in songs
        if session.query(Song).filter_by(filename=song.filename).first() is None
    ]
