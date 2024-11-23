# TODO Create a script which is reading the media files in the linked folder. Put the
#  the filenames into the DB. Update by triggering the script.

import os

from flask import Flask, flash, redirect, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, FormField, FieldList, Form

basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config["SECRET_KEY"] = "Pa$$w0rD"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "data.sqlite"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)


class FileMappingForm(FlaskForm):
    card_identifier = SelectField("Card", choices=["001", "002", "003", "004"])
    file_name = SelectField("File Name", choices=["A", "B", "C", "D"])
    submit = SubmitField("Save")


class Card(db.Model):
    __tablename__ = "cards"
    uid = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64), unique=True)
    audio_file_id = db.Column(db.Integer, db.ForeignKey("audio_files.id"))

    def __repr__(self):
        return f"<Card {self.uid}>"


class AudioFile(db.Model):
    __tablename__ = "audio_files"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(64), unique=True, nullable=False)
    cards = db.relationship("Card", backref="audio_file", lazy="joined")

    def __repr__(self):
        return f"<AudioFile {self.filename}>"


table_header = ("Card Id", "Card Name", "File Name")


def get_cards():
    return (
        db.session.query(Card.uid, Card.name, AudioFile.filename)
        .outerjoin(AudioFile)
        .all()
    )


def get_card_identifier_options() -> list:
    return [(card.uid, " - ".join([card.uid, card.name])) for card in Card.query.all()]


def get_filenames():
    return [
        (audio_file.id, audio_file.filename) for audio_file in AudioFile.query.all()
    ]


@app.route("/", methods=["GET", "POST"])
def index():
    table_data = get_cards()
    form = FileMappingForm()
    card_options = get_card_identifier_options()
    form.card_identifier.choices = card_options
    form.file_name.choices = get_filenames()
    if form.validate_on_submit():
        card = Card.query.filter_by(uid=form.card_identifier.data).first()
        card.audio_file_id = form.file_name.data
        db.session.add(card)
        db.session.commit()
        flash("File mapping successfully updated!")
        return redirect(url_for("index"))
    return render_template(
        "index.html",
        form=form,
        table_header=table_header,
        table_data=table_data,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
