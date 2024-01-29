from flask import g, redirect, url_for, flash, session
from functools import wraps
from app import CURRENT_USER_KEY

################################ Decorator ################################
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash('You need to be logged in to view this page.')
            return redirect(url_for('login'))  
        return f(*args, **kwargs)
    return decorated_function

################################ Other Functions ################################

def perform_login(user):
    """Log in user."""

    session[CURRENT_USER_KEY] = user.id

def perform_logout():
    """Logout user."""

    session.pop(CURRENT_USER_KEY, None)