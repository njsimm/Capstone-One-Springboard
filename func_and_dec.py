import requests
from datetime import datetime
from flask import g, redirect, url_for, flash, session
from functools import wraps
from models import db, Asset, UserAssetComparison
from constants import CURRENT_USER_KEY, CMC_BASE_URL, AV_BASE_URL
from config import CMC_API_KEY, ALPHA_VANTAGE_API_KEY

def login_required(f):
    """
    Decorator that will require a user to be logged in to access a route.
    If the user is not logged in, they will be redirected to the login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash('You need to be logged in to view this page.')
            return redirect(url_for('login'))  
        return f(*args, **kwargs)
    return decorated_function

def perform_login(user):
    """
    Log in user by adding user id to the session.
    """

    session[CURRENT_USER_KEY] = user.id

def perform_logout():
    """
    Logout user by removing user id from the session.
    """

    session.pop(CURRENT_USER_KEY, None)

def get_asset_info(asset_type, ticker):
    """
    Gets asset info from external APIs. 
    Returns a dictionary with the asset's name, ticker, price, and market cap.
    Supports both crypto and stock assets.
    """

    try:
        if asset_type == 'crypto':
            # Get cryptocurrency data from CoinMarketCap API
            params = {'symbol': ticker}
            headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
            response = requests.get(CMC_BASE_URL, headers=headers, params=params)
            data = response.json()

            if 'data' not in data or ticker not in data['data'] or not data['data'][ticker]:
                raise ValueError(f'No data is available for {ticker}')

            # Extract data from response and round the price and market cap to 2 decimal places
            name = data['data'][ticker][0]['name']
            ticker_symbol = data['data'][ticker][0]['symbol']
            price = round(float(data['data'][ticker][0]['quote']['USD']['price']), 2)
            market_cap = round(float(data['data'][ticker][0]['quote']['USD']['market_cap']), 2)

        else:
            # Get stock data from Alpha Vantage API.
            params_1 = {'function': 'GLOBAL_QUOTE', 'symbol': ticker, 'apikey': ALPHA_VANTAGE_API_KEY}
            params_2 = {'function': 'OVERVIEW', 'symbol': ticker, 'apikey': ALPHA_VANTAGE_API_KEY}

            # First request retrives the ticker and price
            response_1 = requests.get(AV_BASE_URL, params=params_1)
            data_1 = response_1.json()

            # Second request retrieves the name and market cap
            response_2 = requests.get(AV_BASE_URL, params=params_2)
            data_2 = response_2.json()

            if '05. price' not in data_1['Global Quote'] or 'MarketCapitalization' not in data_2:
                raise ValueError(f'No data is available for {ticker}')

            # Extract data from response and round the price and market cap to 2 decimal places
            name = data_2['Name']
            ticker_symbol = data_1['Global Quote']['01. symbol']
            price = round(float(data_1['Global Quote']['05. price']), 2)
            market_cap = round(float(data_2['MarketCapitalization']), 2)
    
    except ValueError as exc:
        return {'error': str(exc)}
    
    except requests.exceptions.RequestException as exc:
        return {'error': f"Network error: {exc}"}

    except Exception as exc:
        return {'error': f"Unexpected error: {exc}"}

    return {'name': name, 'ticker': ticker_symbol, 'price': price, 'market_cap': market_cap}

def commit_asset_to_db(asset_dict):
    """
    Commit asset info to db.
    If the asset already exists, update the price and market cap.
    """

    existing_asset = Asset.query.filter_by(ticker=asset_dict['ticker']).first()

    if existing_asset:
        # Update the price and market cap
        existing_asset.price = asset_dict['price']
        existing_asset.market_cap = asset_dict['market_cap']
    else:
        # Add a new asset
        new_asset = Asset(name = asset_dict['name'], ticker = asset_dict['ticker'], price = asset_dict['price'], market_cap = asset_dict['market_cap'])
        
        db.session.add(new_asset)
    
    db.session.commit()

def compare_assets_mc(asset_dict_1, asset_dict_2):
    """
    Compares two assets by market cap.
    Returns a dictionary with the percentage change and multiple between the two assets.
    """

    mc1 = asset_dict_1['market_cap']
    mc2 = asset_dict_2['market_cap']

    percentage_change = round((mc2-mc1) / mc1 * 100, 2)

    if mc1 < mc2:
        multiple = round(mc2 / mc1, 2)

    else:
        multiple_fraction = round(mc2 / mc1, 7)
        multiple = round(1 / multiple_fraction, 2)

    return {'percentage_change': percentage_change, 'multiple': multiple}

def commit_asset_comparison_to_db(asset_dict_1, asset_dict_2, results_dict):
    """
    Commits asset comparison to db.
    Links the comparison to the user and the assets being compared.
    """
    
    asset_1 = Asset.query.filter_by(ticker=asset_dict_1['ticker']).first()
    asset_2 = Asset.query.filter_by(ticker=asset_dict_2['ticker']).first()

    new_comparison = UserAssetComparison(user_id = g.user.id, asset_id_1 = asset_1.id, asset_1_price_at_comparison = asset_dict_1['price'], asset_1_market_cap_at_comparison = asset_dict_1['market_cap'], asset_id_2 = asset_2.id, asset_2_price_at_comparison = asset_dict_2['price'], asset_2_market_cap_at_comparison = asset_dict_2['market_cap'], comparison_timestamp = datetime.now(), percent_difference = results_dict['percentage_change'])

    db.session.add(new_comparison)
    db.session.commit()