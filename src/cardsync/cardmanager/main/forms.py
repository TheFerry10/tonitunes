from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired


class CardPlaylistMappingForm(FlaskForm):
    card_select = SelectField("Card", choices=["001", "002", "003", "004"])
    playlist_select = SelectField("Playlist", choices=["A", "B", "C", "D"])
    submit = SubmitField("Save")


class PlaylistAddSongForm(FlaskForm):
    song_select = SelectField("Song", choices=["01", "02"])
    submit = SubmitField("Add")


class PlaylistForm(FlaskForm):
    name = StringField("Playlist Name", validators=[DataRequired()])
    submit = SubmitField("Create Playlist")
