from flask_wtf import FlaskForm
from wtforms import RadioField, SelectField, StringField, SubmitField
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


class CardInfoForm(FlaskForm):
    image_select = RadioField(
        "Image", choices=["A", "B", "C", "D"], validators=[DataRequired()]
    )
    name = StringField(
        "Card Name",
        validators=[DataRequired()],
    )
    submit = SubmitField("Save")
