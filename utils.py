import requests
import streamlit as st

# Currency conversion utilities

def get_exchange_rates(base_currency="USD"):
    """
    Fetch current exchange rates from a free API
    Returns a dictionary of currency rates
    """
    try:
        # Using exchangerate-api.com (free tier, no API key needed)
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("rates", {})
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching exchange rates: {e}")
        return None

def convert_currency(amount, from_currency, to_currency, rates):
    """
    Convert amount from one currency to another
    """
    if not rates or from_currency == to_currency:
        return amount
    
    try:
        # Convert to USD first, then to target currency
        if from_currency != "USD":
            usd_amount = amount / rates.get(from_currency, 1)
        else:
            usd_amount = amount
        
        if to_currency != "USD":
            converted_amount = usd_amount * rates.get(to_currency, 1)
        else:
            converted_amount = usd_amount
        
        return round(converted_amount, 2)
    except:
        return amount

def get_currency_symbol(currency_code):
    """
    Get currency symbol for display
    """
    symbols = {
        "USD": "$", "EUR": "€", "GBP": "£", "NGN": "₦"
    }
    return symbols.get(currency_code, currency_code)

def get_popular_currencies():
    """
    Return list of popular currencies for the dropdown
    """
    return ["USD", "EUR", "GBP", "NGN"]