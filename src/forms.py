from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, URL, Length, Optional

class RessourceForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=10)])
    link = StringField("Link", validators=[DataRequired(), URL()])
    description = StringField("Description", validators=[Optional()])
    medium = SelectField(
        "Medium", 
        choices=[
            ('Article', 'Article'),
            ('Website', 'Website'),
            ('Study/Paper', 'Study/Paper'),
            ('Tool', 'Tool'),
        ],
        validators=[DataRequired()]
    )

    category = SelectField(
        "Category", 
        choices=[
            ('Programming', 'Programming'),
            ('Design', 'Design'),
            ('Machine Learning', 'Machine Learning'),
            ('Trading', 'Trading'),
            ('Maths', 'Maths'),
        ],
        validators=[DataRequired()]
    )

    topic = SelectField(
        "Topic", 
        choices=[
            ('Security', 'Security'),
            ('Frameworks', 'Frameworks'),
            ('Documentation', 'Documentation'),
            ('Repositories', 'Repositories'),
        ],
        validators=[DataRequired()]
    )

    tags = SelectMultipleField(
        "Tags", 
        choices=[
            ('Must Have', 'Must Have'),
            ('Optional', 'Optional'),
        ],
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
    