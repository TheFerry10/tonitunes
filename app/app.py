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


table_header = ("Card UID", "Card Name", "Connected Song")


class FileNameForm(Form):
    file_name = SelectField(
        label="Dropdown",
        choices=[
            ("option1", "Option 1"),
            ("option2", "Option 2"),
            ("option3", "Option 3"),
        ],
    )


class FileMappingForm(FlaskForm):
    card_identifier = SelectField("Card", choices=["001", "002", "003", "004"])
    file_name = SelectField("File Name", choices=["A", "B", "C", "D"])
    submit = SubmitField("Save")


class TableForm(FlaskForm):
    dropdown_fields = FieldList(FormField(FileNameForm), min_entries=3)
    submit = SubmitField("Submit")


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


def get_card_identifier_options() -> list:
    return [("001", "001 - A"), ("002", "002 - B"), ("003", "003 - C")]


@app.route("/", methods=["GET", "POST"])
def index():

    form = TableForm()
    file_mapping_form = FileMappingForm()
    card_options = get_card_identifier_options()
    print(dir(file_mapping_form))
    file_mapping_form.card_identifier.choices = card_options
    if form.validate_on_submit():
        for value in form.dropdown_fields.data:
            print(value)
        flash("File mapping successfully updated!")
    return render_template("index.html", form=form, file_mapping_form=file_mapping_form)


if __name__ == "__main__":
    app.run(host="localhost", debug=True)
