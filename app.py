import os

from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask_wtf.csrf import validate_csrf
from wtforms import ValidationError
from sqlalchemy.exc import IntegrityError

from config import DATABASE_URI_FALLBACK, SECRET_KEY_FALLBACK
from constants import CURRENT_USER_KEY
from forms import SignupForm, LoginForm, ComparisonForm
from func_and_dec import login_required, perform_login, perform_logout, get_asset_info, commit_asset_to_db, compare_assets_mc, commit_asset_comparison_to_db
from models import User, UserAssetComparison, connect_db, db

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

# User and g
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

# Routes
@app.route('/')
def home_page():
    """If user is logged in, redirect to dashboard. If not, render home page."""
    if g.user:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    Renders the dashboard page.
    Passes the user and the comparison form to the template to be used in the front end.
    """

    user = g.user
    form = ComparisonForm()
    
    return render_template('dashboard.html', user=user, form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handles user signup.
    If user is logged in, redirect to dashboard. If not, render signup page.
    Creates a form instance. If the form is not validated, the signup page is rendered. 
    If the form is validated following input and submission of the information, the user is added to the database and logged in.
    """

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

        perform_login(user)

        return redirect(url_for('dashboard'))
    
    else:
        return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.
    If user is already logged in, redirect to dashboard. If not, render login page.
    Creates a form instance. If the form is not validated, the login page is rendered.
    If the form is validated and the user is authenticated, the user is logged in and redirected to the dashboard.
    If the user is not authenticated, a message is flashed and the login page is rendered.
    """

    if g.user:
        return redirect(url_for('dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(username=form.username.data, entered_login_pwd=form.password.data)
        
        if user:
            perform_login(user)
            return redirect(url_for('dashboard'))
        
        else:
            flash("Incorrect username or password.")
    
    return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    Handles logout of user.
    Logs out the user and redirects to the home page.
    Flashes a goodbye message to the user.
    """

    user = g.user
    perform_logout()
    flash (f"Goodbye, {user.username}!")

    return redirect(url_for('home_page'))

@app.route('/handle_comparison', methods=['POST'])
@login_required
def handle_comparison():
    """
    Handles the comparison form submission.
    Gets the CSRF token from the request and validates it.
    If the CSRF token is invalid, a message is returned and a 400 status code is sent.
    If the CSRF token is valid, both asset types and tickers are retrieved from the request.
    Assets are added to the database and compared, the comparison is added to the database, and the results are returned as a JSON object.
    """
    
    try:
        csrf_token = request.json.get('csrf_token')
        validate_csrf(csrf_token)
    except ValidationError:
        return (jsonify(message="Invalid CSRF token."), 400)

    asset_type_1 = request.json['asset_type_1']
    ticker_1 = request.json['ticker_1']
    asset_type_2 = request.json['asset_type_2']
    ticker_2 = request.json['ticker_2']

    if asset_type_1 == asset_type_2 and ticker_1 == ticker_2:
        return (jsonify(message="Select two different assets."), 422)

    asset_dict_1 = get_asset_info(asset_type_1, ticker_1)

    if 'error' in asset_dict_1:
        return (jsonify(message=asset_dict_1['error']), 400)

    commit_asset_to_db(asset_dict_1)

    asset_dict_2 = get_asset_info(asset_type_2, ticker_2)

    if 'error' in asset_dict_2:
        return (jsonify(message=asset_dict_2['error']), 400)

    commit_asset_to_db(asset_dict_2)

    results_dict = compare_assets_mc(asset_dict_1, asset_dict_2)

    commit_asset_comparison_to_db(asset_dict_1, asset_dict_2, results_dict)

    return (jsonify(results=results_dict), 200)

@app.route('/get_user_history', methods=['GET'])
@login_required
def get_user_history():
    """
    Retrieves the user's comparison history.
    Comparison history is retrieved from the database and returned as a JSON object.
    """
    
    user = g.user
    history = UserAssetComparison.query.filter_by(user_id = user.id).all()
    history_list = [{'comparison_timestamp': comparison.comparison_timestamp, 'name_1': comparison.asset_1.name, 'asset_1_market_cap_at_comparison': float(comparison.asset_1_market_cap_at_comparison),  'name_2': comparison.asset_2.name, 'asset_2_market_cap_at_comparison': float(comparison.asset_2_market_cap_at_comparison), 'percent_difference': float(comparison.percent_difference)} for comparison in history]

    return (jsonify(history=history_list), 200)