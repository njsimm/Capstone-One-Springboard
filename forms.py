from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length


class SignupForm(FlaskForm):
    """Form to allow a user to sign up"""

    username = StringField('Username', validators=[Length(min=4), DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6), DataRequired()])

class LoginForm(FlaskForm):
    """Form to allow a user to login"""

    username = StringField('Username', validators=[Length(min=4), DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])