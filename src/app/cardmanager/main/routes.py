import csv
import os
from pathlib import Path
from typing import List

from flask import (
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename

from ..db import db_session
from ..models import Base, Card, Playlist, Song
from . import main
from .forms import (
    CardInfoForm,
    CardPlaylistMappingForm,
    PlaylistAddSongForm,
    PlaylistForm,
)

app = current_app


@main.route("/", methods=["GET", "POST"])
def index():
    cards = Card.query.all()
    return render_template("index.html", cards=cards)


@main.route("/card/update/<int:card_uid>", methods=["GET", "POST"])
def update_card(card_uid: int):
    card = Card.query.get(card_uid)
    if not card:
        flash("Card not found", category="error")
        return redirect(url_for(".index"))
    image_folder = os.path.join(app.config["STATIC_PATH"], "images/cards")
    available_images = [
        os.path.join("images/cards", filename)
        for filename in os.listdir(image_folder)
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
    ]
    form = CardInfoForm()
    form.image_select.choices = available_images
    if form.validate_on_submit():
        selected_image = form.image_select.data
        selected_name = form.name.data

        if (selected_image == card.image_filename) & (selected_name == card.name):
            return redirect(url_for(".index"))
        card.name = selected_name
        card.image_filename = selected_image
        db_session.add(card)
        db_session.commit()
        flash("Card mapping updated successfully!")
        return redirect(url_for(".index"))

    return render_template(
        "update-card.html", form=form, card=card, available_images=available_images
    )


@main.route("/card/map/<int:card_uid>", methods=["GET", "POST"])
def map_card(card_uid: int):
    card = Card.query.get(card_uid)
    if not card:
        flash("Card not found", category="error")
        return redirect(url_for(".index"))

    form = CardPlaylistMappingForm()
    form.playlist_select.choices = [
        (playlist.id, playlist.name) for playlist in db_session.query(Playlist).all()
    ]

    if form.validate_on_submit():
        card.playlist_id = form.playlist_select.data
        db_session.add(card)
        db_session.commit()
        flash("Card mapping updated successfully!")
        return redirect(url_for(".index"))

    return render_template("map-card.html", form=form, card=card)


@main.route("/playlist/edit/<int:playlist_id>", methods=["GET", "POST"])
def edit_playlist(playlist_id: int):
    """
    Edit a playlist by adding songs to it.
    """
    form = PlaylistAddSongForm()
    artists = [song[0] for song in db_session.query(Song.artist).distinct().all()]
    form.artist_select.choices = [(artist, artist) for artist in artists]
    playlist = db_session.get(Playlist, playlist_id)

    return render_template(
        "playlist-edit.html", form=form, playlist=playlist, artists=artists
    )


@main.route("/playlist/manage", methods=["GET", "POST"])
def manage_playlists():
    form = PlaylistForm()
    if form.validate_on_submit():
        playlist = db_session.query(Playlist).filter_by(name=form.name.data).first()
        if playlist:
            flash(f"Playlist {form.name.data} already exists", category="error")
            return redirect(url_for(".manage_playlists"))
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
        flash(f"Songs file {file_path} does not exist", category="error")
        return redirect(url_for(".index"))

    songs = load_model_instances_from_csv(Song, file_path)
    new_songs = filter_new_songs(songs, db_session)
    if new_songs:
        db_session.add_all(new_songs)
        db_session.commit()
        flash(f"Loaded {len(new_songs)} new songs from {file_path} into the database")
    else:
        flash(f"All songs from {file_path} already exist", category="info")
    return redirect(url_for(".index"))


@main.route("/cards/load", methods=["GET"])
def load_cards():
    file_path = Path(app.config["TONITUNES_CARDS_DIR"], "cards.csv")
    if not file_path.is_file():
        flash(f"Cards file {file_path} does not exist", category="error")
        return redirect(url_for(".index"))

    cards = load_model_instances_from_csv(Card, file_path)
    new_cards = filter_new_cards(cards, db_session)
    if new_cards:
        db_session.add_all(new_cards)
        db_session.commit()
        flash(f"Loaded {len(new_cards)} cards from {file_path} into the database")
    else:
        flash(f"All cards from {file_path} already exist", category="info")
    return redirect(url_for(".index"))


@main.route("/songs/search", methods=["GET"])
def search_songs():
    query = request.args.get("q", "").strip()
    artist = request.args.get("artist", "").strip()
    album = request.args.get("album", "").strip()
    if not query and not artist and not album:
        return jsonify([])

    filters = []
    if query:
        filters.append(
            (Song.title.ilike(f"%{query}%") | Song.album.ilike(f"%{query}%"))
        )
    if artist:
        filters.append(Song.artist.ilike(f"%{artist}%"))

    if album:
        filters.append(Song.album.ilike(f"%{album}%"))

    songs = db_session.query(Song).filter(*filters).all()
    return jsonify(
        [
            {
                "id": song.id,
                "artist": song.artist,
                "title": song.title,
                "album": song.album,
                "filename": song.filename,
                "duration": song.duration,
            }
            for song in songs
        ]
    )


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route("/upload/card/<int:card_uid>", methods=["GET", "POST"])
def upload_file(card_uid: int):
    card = db_session.get(Card, card_uid)
    if not card:
        flash("Card not found", category="error")
        return redirect(url_for(".index"))

    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            UPLOAD_FOLDER = os.path.join(app.config["STATIC_PATH"], "images/cards")

            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(file_path):
                flash("File already exists. Please rename your file and try again.")
                return redirect(request.url)
            file.save(file_path)
            card.image_filename = os.path.join("images/cards/", filename)
            db_session.add(card)
            db_session.commit()
            flash("File successfully uploaded")
            return redirect(url_for(".update_card", card_uid=card.uid))
    return render_template("card-upload.html", card=card)


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
