import os

from flask import Flask, url_for, render_template, redirect, flash, jsonify, request, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User
from forms import SignupForm, LoginForm
from config import DATABASE_URI_FALLBACK, SECRET_KEY_FALLBACK

# Define the key used to store the current user's ID in the session
# This is the key in the session's key-value pair that holds the logged-in user's ID
CURRENT_USER_KEY = "current_user"

from func_and_dec import login_required, login, logout

app = Flask(__name__)

# Get DB_URI (SQLALCHEMY_DATABASE_URI) from environ variable or use the default value.
# Get SECRET_KEY from environ variable or use the default value.
app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', DATABASE_URI_FALLBACK))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', SECRET_KEY_FALLBACK)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

# after configuration, connect the db/app
connect_db(app)

#################### User and g ####################
# This function runs before every request
# If logged in, add current user to Flask global, else add None

@app.before_request
def determine_g():
    """Load user id from session, and save it in Flask's `g` global."""
    user_id = session.get(CURRENT_USER_KEY)

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)


#################### Routes ####################
        
@app.route('/')
def home_page():
    """Home page."""
    if g.user:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@login_required
@app.route('/dashboard')
def dashboard():
    """Dashboard page."""
    return render_template('dashboard.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handle user signup.
    Create new user and add to DB. Redirect to dashboard.
    If form not valid, present form.
    If user already exists with that username: flash message and re-present form.
    """

    # If user is logged in, redirect to dashboard
    if g.user:
        return redirect(url_for('dashboard'))
    
    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(username=form.username.data, password=form.password.data)

            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            flash("Username taken. Please pick another")
            return render_template('signup.html', form=form)
        
        # Log in user by adding user's ID to the session if the user successfully signs up
        login(user)

        return redirect(url_for('dashboard'))
    
    else:
        return render_template('signup.html', form=form)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""

    # If user is logged in, redirect to dashboard
    if g.user:
        return redirect(url_for('dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(username=form.username.data, password=form.password.data)
        
        if user:
            # Log in user by adding user's ID to the session
            login(user)
            return redirect(url_for('dashboard'))
        
        else:
            flash("Incorrect username or password.")
    
    return render_template('login.html', form=form)


@app.route('/logout', methods=['POST'])
def logout():
    """Handle logout of user."""

    # Log out user by removing user's ID from the session
    user = g.user
    logout()
    flash (f"Goodbye, {user.username}!")

    return redirect(url_for('home_page'))