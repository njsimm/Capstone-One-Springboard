from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()  # Creates SQLAlchemy's instance for database interaction
bcrypt = Bcrypt()  # Creates Bcrypt's instance for password hashing

def connect_db(app):
    """
    Connects the Flask app to the SQLAlchemy database.
    """
    db.app = app
    db.init_app(app)
    
class User(db.Model):
    """
    User model for representing a user in the database.
    """

    __tablename__ = 'users'

    def __repr__(self):
        """Shows info about user."""
        u = self
        return f"<User: id={u.id}, Username={u.username}>"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String(50), nullable=False, unique=True)

    password = db.Column(db.String(72), nullable=False)

    @classmethod
    def signup(cls, username, password):
        """
        - Returns instance of user w/ hashed password. This instance of user is not yet added to the database, but will be added and commited to the database in the app.py file using a form (FLASK WTF).
        """

        # Generate a hashed version of the password using bcrypt. This returns a bytestring. We need to decode it into a normal (Unicode utf8) string before passing it to create an instance of the user
        hashed_pwd = bcrypt.generate_password_hash(password)

        # Decode the bytestring into a normal (Unicode) string using utf8 encoding. This makes it easier to store and handle.
        hashed_utf8_pwd = hashed_pwd.decode('utf8')

        # Return instance of user w/ hashed password and all other info from the form.
        return cls(username=username, password=hashed_utf8_pwd)
    
    @classmethod
    def authenticate(cls, username, entered_login_pwd):
        """
        - Validate that user exists and password is correct
        - Return user if valid; else return false
        - entered_login_pwd is the password that the user is trying to log in with; user.password is the hashed password that is stored in the database and is being compared to the entered_login_pwd
        """
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, entered_login_pwd):
            # return user instance
            return user
        else:
            return False

class Asset(db.Model):
    """
    Asset model for representing an asset in the database.
    """

    __tablename__ = 'assets'

    def __repr__(self):
        """Shows info about asset."""
        a = self
        return f"<Asset: id={a.id}, Name={a.name}, Ticker={a.ticker}, Price={a.price}, Market Cap={a.market_cap}>"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(50), nullable=False, unique=True)

    ticker = db.Column(db.String(10), nullable=False, unique=True)

    price = db.Column(db.Numeric(precision=16, scale=2), nullable=False)

    market_cap = db.Column(db.Numeric(precision=16, scale=2), nullable=False)

class UserAssetComparison(db.Model):
    """
    User Asset Comparison model for representing a comparison by a user in the database.
    """

    __tablename__ = 'users_assets_comparisons'

    def __repr__(self):
        """Shows info about user asset comparison."""

        uac = self
        return f"<UserAssetComparison: id={uac.id}, User ID={uac.user_id}, Asset ID 1={uac.asset_id_1}, Asset 1 Price={uac.asset_1_price_at_comparison}, Asset 1 Market Cap={uac.asset_1_market_cap_at_comparison}, Asset ID 2={uac.asset_id_2}, Asset 2 Price={uac.asset_2_price_at_comparison}, Asset 2 Market Cap={uac.asset_2_market_cap_at_comparison}, Comparison Timestamp={uac.comparison_timestamp}, Percent Difference={uac.percent_difference}>"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)

    asset_id_1 = db.Column(db.Integer, db.ForeignKey('assets.id', ondelete='cascade'), nullable=False)

    asset_1_price_at_comparison = db.Column(db.Numeric(precision=16, scale=2), nullable=False)

    asset_1_market_cap_at_comparison = db.Column(db.Numeric(precision=16, scale=2), nullable=False)

    asset_id_2 = db.Column(db.Integer, db.ForeignKey('assets.id', ondelete='cascade'), nullable=False)

    asset_2_price_at_comparison = db.Column(db.Numeric(precision=16, scale=2), nullable=False)

    asset_2_market_cap_at_comparison = db.Column(db.Numeric(precision=16, scale=2), nullable=False)

    comparison_timestamp = db.Column(db.DateTime, nullable=False)

    percent_difference = db.Column(db.Numeric(precision=16, scale=2), nullable=False)

    # Relationships
    asset_1 = db.relationship('Asset', foreign_keys=[asset_id_1], backref='comparison_as_asset_1')
    
    asset_2 = db.relationship('Asset', foreign_keys=[asset_id_2], backref='comparison_as_asset_2')