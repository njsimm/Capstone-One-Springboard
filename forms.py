from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField
from wtforms.validators import DataRequired, Length


class SignupForm(FlaskForm):
    """Form to allow a user to sign up"""

    username = StringField('Username', validators=[Length(min=4), DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6), DataRequired()])

class LoginForm(FlaskForm):
    """Form to allow a user to login"""

    username = StringField('Username', validators=[Length(min=4), DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class ComparisonForm(FlaskForm):
    """Form to allow a user to compare to assets"""

    asset_type_1 = RadioField('Asset Type', choices=[('crypto', 'Crypto'), ('stock', 'Stock')], validators=[DataRequired()])
    ticker_1 = StringField('Ticker', validators=[DataRequired()])

    asset_type_2 = RadioField('Asset Type', choices=[('crypto', 'Crypto'), ('stock', 'Stock')], validators=[DataRequired()])
    ticker_2 = StringField('Ticker', validators=[DataRequired()])