from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

EXPIRATION_CHOICES_SECONDS = [
    ("", "Never"),
    ("600", "10 Minutes"),
    ("3600", "1 Hour"),
    ("86400", "1 Day"),
    ("604800", "1 Week"),
    ("2592000", "1 Month"),
]

LANGUAGE_CHOICES = [
    ("text", "Plain Text"),
    ("python", "Python"),
    ("javascript", "JavaScript"),
    ("bash", "Bash"),
    ("json", "JSON"),
    ("html", "HTML"),
    ("css", "CSS"),
    ("sql", "SQL"),
    ("yaml", "YAML"),
    ("markdown", "Markdown"),
]


class CreatePasteForm(FlaskForm):
    content = TextAreaField("content", validators=[DataRequired()])
    title = StringField("title", validators=[Optional(), Length(max=255)])
    expiration = SelectField("expiration", choices=EXPIRATION_CHOICES_SECONDS, default="")
    language = SelectField("language", choices=LANGUAGE_CHOICES, default="text")
