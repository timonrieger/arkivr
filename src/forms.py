from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField, RadioField
from wtforms.validators import DataRequired, URL, Length, Optional
from src.constants import MEDIUM_CHOICES, CATEGORY_CHOICES, TAGS_CHOICES

class RessourceForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=20)])
    link = StringField("Link", validators=[DataRequired(), URL()])
    description = StringField("Description", validators=[DataRequired()])
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

    tags = SelectMultipleField(
        "Tags", 
        choices=TAGS_CHOICES,
        validators=[Optional()],
        render_kw={"style": "height: 300px"}
    )
    private = RadioField(
        "Private?",
        choices=[(True, "Yes, make it private"), (False, "No, make it public")],
        validators=[DataRequired()])
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
    
    
class PasswordResetForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired()])
    submit = SubmitField(label="Reset Password")
    