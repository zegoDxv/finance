import os
import requests
import urllib.parse


from flask import redirect, render_template, request, session, url_for
from functools import wraps

# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if session.get("userd_id") is None:
#             return redirect("/login")
#         return f(*args, **kwargs)
#     return decorated_function


# Checking if user is logged in
def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if "user_id" in session:
            return f(*args, *kwargs)
        else:
            return redirect (url_for("login"))
        
    return wrap

# Finding the current Symbol of quote

def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = "pk_d31d365a0c5943c6834e435023f5f521"
        # response = requests.get(f"https://api.iex.cloud/v1/data/core/quote/{symbol}?token={api_key}")
        response = requests.get(f"https://api.iex.cloud/v1/data/core/quote/{symbol}?token={api_key}")
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        data = {
            "name": quote[0]["companyName"],
            "price": float(quote[0]["latestPrice"]),
            "symbol": quote[0]["symbol"]
        }
        return data
    except (KeyError, TypeError, ValueError):
        return None

    #   ^
    #   |
    #   |
    #  works
    # api_key = "sk_1e005b3d798342738da3372f5b8580b4"
    # url = f"https://api.iex.cloud/v1/data/core/quote/{symbol}?token={api_key}"
    # response = requests.get(url)
    # return response.json()
