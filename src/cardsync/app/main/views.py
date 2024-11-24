from flask import flash, redirect, render_template, url_for

from ..database import db_session
from ..models import AudioFile, Card
from . import main
from .forms import FileMappingForm


def get_cards():
    return (
        db_session.query(Card.uid, Card.name, AudioFile.filename)
        .outerjoin(AudioFile)
        .all()
    )


def get_card_identifier_options() -> list:
    return [(card.uid, " - ".join([card.uid, card.name])) for card in Card.query.all()]


def get_filenames():
    return [
        (audio_file.id, audio_file.filename) for audio_file in AudioFile.query.all()
    ]


table_header = ("Card Id", "Card Name", "File Name")


@main.route("/", methods=["GET", "POST"])
def index():
    table_data = get_cards()
    form = FileMappingForm()
    card_options = get_card_identifier_options()
    form.card_identifier.choices = card_options
    form.file_name.choices = get_filenames()
    if form.validate_on_submit():
        card = Card.query.filter_by(uid=form.card_identifier.data).first()
        card.audio_file_id = form.file_name.data
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
