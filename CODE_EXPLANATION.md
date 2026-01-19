# Code Explanation for Beginners 📚

This document explains how the Smart Budget App works, making it easy for beginners to understand each part of the code.

## Project Overview

The app has 3 main files:
- `app.py` - Main application (the user interface)
- `utils.py` - Helper functions for currency conversion
- `database.db` - SQLite database (created automatically)

## File-by-File Breakdown

### 1. app.py (Main Application)

#### Imports and Setup
```python
import sqlite3          # For database operations
import streamlit as st  # For web interface
import pandas as pd     # For data manipulation
from utils import ...   # Our custom currency functions
```

#### Database Creation
```python
conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        date TEXT,
        amount REAL,
        category TEXT,
        note TEXT
    )
""")
```
**What this does**: Creates a table to store expenses if it doesn't exist yet.

#### Currency Selection
```python
selected_currency = st.sidebar.selectbox("Select Currency", currencies)
exchange_rates = fetch_rates()
```
**What this does**: 
- Shows a dropdown in the sidebar for currency selection
- Fetches current exchange rates from the internet

#### Adding Expenses
```python
if st.button("➕ Add Expense"):
    usd_amount = convert_currency(amount, selected_currency, "USD", exchange_rates)
    cursor.execute("INSERT INTO expenses (...) VALUES (...)")
```
**What this does**:
- When user clicks "Add Expense", converts their amount to USD
- Stores the expense in the database (always in USD for consistency)

#### Displaying Data
```python
df = pd.read_sql("SELECT * FROM expenses ORDER BY date DESC", conn)
df['display_amount'] = df['amount'].apply(lambda x: convert_currency(...))
```
**What this does**:
- Reads all expenses from database
- Converts amounts from USD to user's selected currency for display

### 2. utils.py (Currency Functions)

#### Getting Exchange Rates
```python
def get_exchange_rates(base_currency="USD"):
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
    response = requests.get(url, timeout=5)
    return response.json().get("rates", {})
```
**What this does**: 
- Contacts a free API to get current currency exchange rates
- Returns a dictionary like `{"EUR": 0.85, "GBP": 0.73, ...}`

#### Converting Currency
```python
def convert_currency(amount, from_currency, to_currency, rates):
    if from_currency != "USD":
        usd_amount = amount / rates.get(from_currency, 1)
    else:
        usd_amount = amount
    
    if to_currency != "USD":
        converted_amount = usd_amount * rates.get(to_currency, 1)
    else:
        converted_amount = usd_amount
```
**What this does**:
- Converts any currency to any other currency
- Always goes through USD as the base currency
- Example: EUR → USD → JPY

#### Currency Symbols
```python
def get_currency_symbol(currency_code):
    symbols = {"USD": "$", "EUR": "€", "GBP": "£", ...}
    return symbols.get(currency_code, currency_code)
```
**What this does**: Returns the proper symbol for each currency ($ for USD, € for EUR, etc.)

## How Data Flows Through the App

1. **User Input**: User enters expense in their preferred currency
2. **Conversion**: App converts to USD using current exchange rates
3. **Storage**: Expense stored in database in USD
4. **Display**: When showing data, converts from USD back to user's currency
5. **Charts**: Creates visual charts using the converted amounts

## Key Programming Concepts Used

### 1. Database Operations (SQLite)
```python
conn = sqlite3.connect("database.db")  # Connect to database
cursor = conn.cursor()                 # Create cursor for operations
cursor.execute("INSERT INTO ...")      # Run SQL command
conn.commit()                          # Save changes
conn.close()                          # Close connection
```

### 2. API Calls
```python
response = requests.get(url, timeout=5)  # Make HTTP request
data = response.json()                   # Parse JSON response
```

### 3. Error Handling
```python
try:
    # Code that might fail
    response = requests.get(url)
except Exception as e:
    # What to do if it fails
    st.error(f"Error: {e}")
```

### 4. Streamlit Components
```python
st.title("My App")                    # Page title
st.sidebar.selectbox(...)             # Dropdown in sidebar
st.number_input(...)                  # Number input field
st.button("Click me")                 # Button
st.dataframe(df)                      # Display table
st.bar_chart(data)                    # Display chart
```

### 5. Data Processing with Pandas
```python
df = pd.read_sql("SELECT * FROM ...", conn)  # Read from database
df.groupby("category")["amount"].sum()       # Group and sum data
df.apply(lambda x: convert_currency(...))    # Apply function to each row
```

## Why We Store in USD

**Problem**: If we stored expenses in different currencies, it would be hard to:
- Calculate totals when you have expenses in EUR, USD, and JPY
- Create accurate charts and summaries

**Solution**: 
- Store everything in USD (universal base currency)
- Convert to user's preferred currency only for display
- This keeps calculations consistent and accurate

## API Integration Benefits

**Without API**: App would only work with one currency
**With API**: 
- Support for 160+ currencies
- Real-time exchange rates
- Automatic conversion
- Better user experience

## Error Handling Strategy

The app handles several potential errors:
- **No internet**: Falls back to USD-only mode
- **API failure**: Shows warning but continues working
- **Invalid input**: Shows error messages to guide user
- **Database issues**: Creates new database if needed

## Beginner Modifications You Can Try

### Easy Changes:
1. **Add new categories**: Modify the category list in `app.py`
2. **Change colors**: Add Streamlit color parameters
3. **Add more currencies**: Extend the currency list in `utils.py`

### Medium Changes:
1. **Add expense editing**: Create update/delete functionality
2. **Add date filtering**: Filter expenses by date range
3. **Export data**: Add CSV download feature

### Advanced Changes:
1. **User accounts**: Add login system
2. **Expense predictions**: Use data to predict future spending
3. **Receipt scanning**: Add image upload and OCR

## Learning Path

1. **Start here**: Understand how Streamlit creates web interfaces
2. **Next**: Learn SQLite database operations
3. **Then**: Study API integration with requests library
4. **Finally**: Explore pandas for data analysis

## Useful Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLite Tutorial](https://www.sqlitetutorial.net/)
- [Pandas Guide](https://pandas.pydata.org/docs/user_guide/)
- [Python Requests](https://requests.readthedocs.io/)

---

**Remember**: The best way to learn is by experimenting! Try modifying small parts of the code and see what happens. 🚀