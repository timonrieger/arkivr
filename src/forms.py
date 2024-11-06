from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, URL, Length, Optional
from constants import MEDIUM_CHOICES, CATEGORY_CHOICES, TOPIC_CHOICES, TAGS_CHOICES

class RessourceForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=20)])
    link = StringField("Link", validators=[DataRequired(), URL()])
    description = StringField("Description", validators=[Optional()])
    medium = SelectField(
        "Medium", 
        choices=MEDIUM_CHOICES,
        validators=[DataRequired()]
    )

    category = SelectField(
        "Category", 
        choices=CATEGORY_CHOICES,
        validators=[DataRequired()]
    )

    topic = SelectField(
        "Topic", 
        choices=TOPIC_CHOICES,
        validators=[DataRequired()]
    )

    tags = SelectMultipleField(
        "Tags", 
        choices=TAGS_CHOICES,
        validators=[Optional()]
    )
    submit = SubmitField(label="Save")


class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired()])
    password = StringField(label="Password", validators=[DataRequired()])
    submit = SubmitField(label="Login")


class RegistrationForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    email = StringField(label="Email", validators=[DataRequired()])
    password = StringField(label="Password", validators=[DataRequired()])
    submit = SubmitField(label="Register")
    