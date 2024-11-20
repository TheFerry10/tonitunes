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


@app.route("/", methods=["GET", "POST"])
def index():

    form = TableForm()
    if form.validate_on_submit():
        for value in form.dropdown_fields.data:
            print(value)
        flash("File mapping successfully updated!")
    return render_template(
        "index.html",
        form=form,
    )


if __name__ == "__main__":
    app.run(host="localhost", debug=True)
