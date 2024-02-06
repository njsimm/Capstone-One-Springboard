# This file is used to store constants that are used throughout the application.
# This allows for easy access to these constants from any file in the application.

# Define the key used to store the current user's ID in the session
# This is the key in the session's key-value pair that holds the logged-in user's ID
CURRENT_USER_KEY = "current_user"

# Base URL for the CoinMarketCap API. 
# This is used for the cryptocurrency data.
CMC_BASE_URL = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'

# Base URL for the Alpha Vantage API.
# This is used for the stock data.
AV_BASE_URL = 'https://www.alphavantage.co/query'