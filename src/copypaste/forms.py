from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class CreatePasteForm(FlaskForm):
    content = TextAreaField("content", validators=[DataRequired()])
    title = StringField("title", validators=[Optional(), Length(max=255)])
