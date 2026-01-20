import requests  # Library for making HTTP requests to APIs
import streamlit as st  # Streamlit library for web app interface

# Currency conversion utilities


def get_exchange_rates(base_currency="USD"):
    """
    Fetch current exchange rates from a free API

    Args:
        base_currency (str): The base currency to get rates for (default: USD)

    Returns:
        dict: Dictionary of currency rates or None if API fails
    """
    try:
        # Using exchangerate-api.com (free tier, no API key needed)
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        # Make HTTP GET request with 5 second timeout
        response = requests.get(url)

        # Check if request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()  # Parse JSON response
            return data.get("rates", {})  # Return rates dictionary
        else:
            return None  # Return None if request failed
    except Exception as e:
        # Display error message in Streamlit sidebar
        st.error(f"Error fetching exchange rates: {e}")
        return None  # Return None if any exception occurs


def convert_currency(amount, from_currency, to_currency, rates):
    """
    Convert amount from one currency to another using exchange rates

    Args:
        amount (float): Amount to convert
        from_currency (str): Source currency code (e.g., 'USD')
        to_currency (str): Target currency code (e.g., 'EUR')
        rates (dict): Dictionary of exchange rates

    Returns:
        float: Converted amount rounded to 2 decimal places
    """
    # If no rates available or same currency, return original amount
    if not rates or from_currency == to_currency:
        return amount

    try:
        # Convert to USD first (base currency), then to target currency
        if from_currency != "USD":
            # Convert from source currency to USD
            usd_amount = amount / rates.get(from_currency, 1)
        else:
            # Already in USD
            usd_amount = amount

        if to_currency != "USD":
            # Convert from USD to target currency
            converted_amount = usd_amount * rates.get(to_currency, 1)
        else:
            # Target is USD, no further conversion needed
            converted_amount = usd_amount

        return round(converted_amount, 2)  # Round to 2 decimal places
    except:
        # Return original amount if conversion fails
        return amount


def get_currency_symbol(currency_code):
    """
    Get currency symbol for display purposes

    Args:
        currency_code (str): Currency code (e.g., 'USD', 'EUR')

    Returns:
        str: Currency symbol or currency code if symbol not found
    """
    # Dictionary mapping currency codes to their symbols
    symbols = {
        "USD": "$",  # US Dollar
        "EUR": "€",  # Euro
        "GBP": "£",  # British Pound
        "NGN": "₦",  # Nigerian Naira
        "JPY": "¥",  # Japanese Yen
        "CAD": "C$",  # Canadian Dollar
        "AUD": "A$",  # Australian Dollar
    }
    # Return symbol if found, otherwise return currency code
    return symbols.get(currency_code, currency_code)


def get_popular_currencies():
    """
    Return list of popular currencies for the dropdown selection

    Returns:
        list: List of currency codes
    """
    # List of commonly used currencies
    return ["USD", "EUR", "GBP", "NGN", "JPY", "CAD", "AUD"]
