from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired


class FileMappingForm(FlaskForm):
    card_identifier = SelectField("Card", choices=["001", "002", "003", "004"])
    file_name = SelectField("File Name", choices=["A", "B", "C", "D"])
    submit = SubmitField("Save")


class PlaylistAddSongForm(FlaskForm):
    playlist_identifier = SelectField("Playlist", choices=["A", "B"])
    song_selection = SelectField("Song", choices=["01", "02"])
    submit = SubmitField("Add")


class PlaylistForm(FlaskForm):
    name = StringField("Playlist Name", validators=[DataRequired()])
    submit = SubmitField("Create Playlist")
