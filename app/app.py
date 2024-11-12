import os

from flask import Flask, flash, redirect, render_template, session, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField

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

table_header = ("Name", "Age", "Country", "NewCountry")
table_data = (
    ("Alice", 30, "USA"),
    ("Bob", 25, "Canada"),
    ("Charlie", 40, "UK"),
)
file_names = ("USA", "UK", "Germany", "")


class FilePathForm(FlaskForm):
    file_path = SelectField(
        "FileName",
        choices=[("song1", "Song 1"), ("song2", "Song 2"), ("song3", "Song 3")],
        default="song2",
    )
    submit = SubmitField("Save")


class Card(db.Model):
    __tablename__ = "card"
    uid = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return "<Card %r>" % self.name


@app.route("/", methods=["GET", "POST"])
def index():
    forms = {"uid0": FilePathForm(), "uid1": FilePathForm()}
    for key, form in forms.items():
        if form.validate_on_submit():
            file_path = form.file_path.data
            print(key, file_path)
            flash("File mapping successfully updated!")
            return redirect(url_for("index"))
    return render_template(
        "index.html",
        table_header=table_header,
        table_data=table_data,
        file_names=file_names,
        forms=forms,
    )


if __name__ == "__main__":
    app.run(host="localhost", debug=True)
