from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, URL, Length, Optional
import requests

NPOINT = "https://api.npoint.io/1ba4f8744068b81b8070"
medium_choices = requests.get(url=NPOINT).json()["medium"]
category_choices = requests.get(url=NPOINT).json()["category"]
topic_choices = requests.get(url=NPOINT).json()["topic"]
tags_choices = requests.get(url=NPOINT).json()["tags"]


class RessourceForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=10)])
    link = StringField("Link", validators=[DataRequired(), URL()])
    description = StringField("Description", validators=[Optional()])
    medium = SelectField(
        "Medium", 
        choices=medium_choices,
        validators=[DataRequired()]
    )

    category = SelectField(
        "Category", 
        choices=category_choices,
        validators=[DataRequired()]
    )

    topic = SelectField(
        "Topic", 
        choices=topic_choices,
        validators=[DataRequired()]
    )

    tags = SelectMultipleField(
        "Tags", 
        choices=tags_choices,
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
    