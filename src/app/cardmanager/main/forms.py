from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired


class CardPlaylistMappingForm(FlaskForm):
    playlist_select = SelectField("Playlist", choices=["A", "B", "C", "D"])
    submit = SubmitField("Save")


class PlaylistAddSongForm(FlaskForm):
    artist_select = SelectField(
        "Artist",
    )


class PlaylistForm(FlaskForm):
    name = StringField("Playlist Name", validators=[DataRequired()])
    submit = SubmitField("Create Playlist")
