# TODO Create a script which is reading the media files in the linked folder. Put the
#  the filenames into the DB. Update by triggering the script.

import os

from flask import Flask, flash, redirect, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField

from adapters.repository import SqlAlchemyUIDMappingRepositoriy
from adapters.rfid_interface import AbstractRFIDModule, RFIDData, TagRegister

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATABASE_URI = "sqlite:///" + os.path.join(basedir, "data.sqlite")

app = Flask(__name__)
app.config["SECRET_KEY"] = "Pa$$w0rD"
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)


class FakeRFIDModule(AbstractRFIDModule):
    def __init__(self):
        self.previous_response = None
        self.current_response = None
        self.event = RFIDData()

    def read(self) -> RFIDData:
        return self.event

    def write(self, text: str):
        pass

    def cleanup(self):
        pass


class Card(db.Model):
    __tablename__ = "cards"
    uid = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64))
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


class FileMappingForm(FlaskForm):
    card_identifier = SelectField("Card", choices=["001", "002", "003", "004"])
    file_name = SelectField("File Name", choices=["A", "B", "C", "D"])
    submit = SubmitField("Save")


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


class CardReaderForm(FlaskForm):
    start = SubmitField("Start")
    # stop = SubmitField("Stop")


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


@app.route("/register", methods=["GET", "POST"])
def register():
    rifd_data_samples = [
        RFIDData(uid="10000009"),
        RFIDData(uid="10000010"),
    ]
    mapping = {
        "10000009": "name_X",
        "10000010": "name_Y",
        "10000005": "name_Z",
    }
    registry = SqlAlchemyUIDMappingRepositoriy(db.session)
    rfid_module = FakeRFIDModule()
    tag_registry = TagRegister(registry, rfid_module, mapping)
    for rifd_data in rifd_data_samples:
        rfid_module.event = rifd_data
        tag_registry.register()
    return render_template("register.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
