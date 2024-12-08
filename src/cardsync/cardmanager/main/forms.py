from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField


class FileMappingForm(FlaskForm):
    card_identifier = SelectField("Card", choices=["001", "002", "003", "004"])
    file_name = SelectField("File Name", choices=["A", "B", "C", "D"])
    submit = SubmitField("Save")
