# Smart Budget App 💰

A beginner-friendly budget tracking application built with Python and Streamlit that helps you manage your expenses with multi-currency support. **Set your budget first, then track expenses interactively!**

## Features ✨

- **Interactive Budget Setup**: Set your monthly budget before tracking expenses
- **Step-by-Step Flow**: Guided process from budget setting to expense tracking
- **Add Expenses**: Track your daily expenses with categories
- **Currency Conversion**: Convert your budget and expenses to different currencies
- **Visual Analytics**: See your spending patterns with charts and progress bars
- **Budget Alerts**: Get warnings when you exceed your budget
- **Data Persistence**: All data is stored locally in SQLite database
- **Real-time Updates**: See budget status update as you add expenses

## What You'll Learn 📚

This project demonstrates:
- **Web App Development** with Streamlit
- **Database Operations** with SQLite (two tables: expenses and budget)
- **API Integration** for currency conversion
- **Data Visualization** with charts and progress bars
- **Session State Management** for interactive flows
- **File Structure** organization

## Installation & Setup 🚀

### Prerequisites
- Python 3.7 or higher
- Internet connection (for currency conversion)

### Step 1: Clone or Download
Download this project to your computer.

### Step 2: Install Dependencies
Open terminal/command prompt in the project folder and run:
```bash
pip install -r requirements.txt
```

### Step 3: Run the App
```bash
streamlit run app.py
```

The app will open in your web browser at `http://localhost:8501`

## How to Use 📖

### Interactive 3-Step Process:

#### Step 1: Set Your Monthly Budget 🎯
1. When you first open the app, you'll be prompted to set a monthly budget
2. Enter your budget amount in your preferred currency
3. Click "Save Budget" to proceed
4. You can update your budget anytime by clicking "Update Budget"

#### Step 2: Add Your Expenses ➕
1. Select the date of your expense
2. Enter the amount spent
3. Choose a category (Food, Transport, Rent, Bills, Entertainment, Shopping, Healthcare, Other)
4. Add an optional note
5. Click "Add Expense"

#### Step 3: Monitor Your Budget Status 📊
1. View all your expenses in a clean table
2. See your total spending vs budget with a progress bar
3. Get alerts if you're over budget
4. View spending breakdown by category with percentages
5. Analyze patterns with interactive charts

### Currency Conversion
1. Select your preferred currency from the sidebar dropdown
2. Your budget and expenses will automatically convert
3. Rates are fetched in real-time from a free API
4. Works with USD, EUR, GBP, NGN, JPY, CAD, AUD

## Project Structure 📁

```
smart_budget_app/
├── app.py              # Main application file
├── utils.py            # Currency conversion utilities
├── database.db         # SQLite database (created automatically)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Detailed Code Explanation 🔍

### app.py - Main Application (Line by Line)

**Lines 1-10: Imports and Dependencies**
```python
import sqlite3          # Database operations
import streamlit as st   # Web app framework
import pandas as pd      # Data manipulation
from utils import (      # Import our custom functions
    get_exchange_rates,  # Fetch currency rates
    convert_currency,    # Convert between currencies
    get_currency_symbol, # Get currency symbols
    get_popular_currencies, # Get supported currencies
)
```

**Lines 12-35: Database Initialization**
```python
# Create connection to SQLite database file
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create expenses table if it doesn't exist
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,    # Auto-incrementing ID
        date TEXT,                # Expense date as text
        amount REAL,              # Amount in USD (for consistency)
        category TEXT,            # Expense category
        note TEXT                 # Optional note
    )
    """
)

# Create budget table for monthly budget storage
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS budget (
        id INTEGER PRIMARY KEY,   # Auto-incrementing ID
        month TEXT UNIQUE,        # Month in YYYY-MM format
        amount REAL,              # Budget amount
        currency TEXT             # Currency of the budget
    )
    """
)
conn.commit()  # Save changes
conn.close()   # Close connection
```

**Lines 37-45: Streamlit Configuration**
```python
# Configure the web page
st.set_page_config(page_title="Smart Budget App", page_icon="💰")
st.title("💰 Smart Budget App")  # Main title
st.markdown("*Set your budget first, then track expenses with multi-currency support*")
```

**Lines 47-65: Currency Setup**
```python
# Sidebar for currency selection
st.sidebar.header("Currency Settings")
currencies = get_popular_currencies()  # Get list from utils.py
selected_currency = st.sidebar.selectbox(
    "Select Currency",
    currencies,
    index=0,  # Default to first currency (USD)
    help="Choose your preferred currency for display",
)

# Cache exchange rates for 1 hour to improve performance
@st.cache_data(ttl=3600)
def fetch_rates():
    return get_exchange_rates()  # Call API function from utils.py

exchange_rates = fetch_rates()  # Get current rates
currency_symbol = get_currency_symbol(selected_currency)  # Get symbol
```

**Lines 67-75: Connection Status**
```python
# Show user if currency conversion is working
if exchange_rates:
    st.sidebar.success(f"✅ Exchange rates updated")
else:
    st.sidebar.warning("⚠️ Using offline mode (USD only)")
    selected_currency = "USD"  # Fallback to USD
    currency_symbol = "$"
```

**Lines 77-120: Budget Setup (Step 1)**
```python
# Import datetime to get current month
import datetime
current_month = datetime.datetime.now().strftime("%Y-%m")  # Format: 2024-01

# Check if budget exists for current month
conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute("SELECT amount, currency FROM budget WHERE month = ?", (current_month,))
budget_data = cursor.fetchone()  # Get first result or None
conn.close()

if budget_data:
    # Budget exists - show it
    budget_amount, budget_currency = budget_data
    # Convert to selected currency if needed
    display_budget = (
        convert_currency(budget_amount, budget_currency, selected_currency, exchange_rates)
        if exchange_rates and budget_currency != selected_currency
        else budget_amount
    )
    st.success(f"✅ Monthly budget set: {currency_symbol}{display_budget:.2f}")
else:
    # No budget - prompt user to set one
    st.warning("⚠️ Please set your monthly budget first before adding expenses")
    st.session_state.update_budget = True  # Flag to show budget form
```

**Lines 122-150: Budget Input Form**
```python
# Show budget form if needed
if st.session_state.get('update_budget', False):
    with st.form("budget_form"):  # Form prevents rerun on every input
        st.subheader("Set Monthly Budget")
        budget_input = st.number_input(
            f"Budget Amount ({currency_symbol})",
            min_value=0.0,
            step=10.0,
            help=f"Enter your monthly budget in {selected_currency}"
        )
        
        if st.form_submit_button("💾 Save Budget", type="primary"):
            if budget_input > 0:
                # Save budget to database
                conn = sqlite3.connect("database.db")
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO budget (month, amount, currency) VALUES (?, ?, ?)",
                    (current_month, budget_input, selected_currency)
                )
                conn.commit()
                conn.close()
                st.success(f"✅ Budget of {currency_symbol}{budget_input} saved!")
                st.session_state.update_budget = False  # Hide form
                st.rerun()  # Refresh page
```

**Lines 152-200: Expense Input (Step 2)**
```python
# Only show expense input if budget is set
if budget_data or st.session_state.get('update_budget', False) == False:
    st.header("➕ Step 2: Add Your Expenses")
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Date input widget
        date = st.date_input("Date", help="Select the date of your expense")
        # Number input with currency symbol
        amount = st.number_input(
            f"Amount ({currency_symbol})",
            min_value=0.0,
            step=0.01,
            help=f"Enter amount in {selected_currency}",
        )
    
    with col2:
        # Category dropdown
        category = st.selectbox(
            "Category",
            ["Food", "Transport", "Rent", "Bills", "Entertainment", "Shopping", "Healthcare", "Other"],
            help="Choose the expense category",
        )
        # Optional text input
        note = st.text_input("Note (Optional)", help="Add any additional details")
    
    # Submit button
    if st.button("➕ Add Expense", type="primary"):
        if amount > 0:
            # Convert to USD for consistent storage
            usd_amount = (
                convert_currency(amount, selected_currency, "USD", exchange_rates)
                if exchange_rates
                else amount
            )
            
            # Insert into database
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO expenses (date, amount, category, note) VALUES (?, ?, ?, ?)",
                (date, usd_amount, category, note),
            )
            conn.commit()
            conn.close()
            st.success(f"✅ Expense of {currency_symbol}{amount} added successfully!")
            st.rerun()  # Refresh to show new data
```

**Lines 202-230: Expense Display (Step 3)**
```python
# Load and display all expenses
st.header("📊 Step 3: Your Expenses & Budget Status")

conn = sqlite3.connect("database.db")
df = pd.read_sql("SELECT * FROM expenses ORDER BY date DESC", conn)
conn.close()

if not df.empty:
    # Convert USD amounts to selected currency
    if exchange_rates and selected_currency != "USD":
        df["display_amount"] = df["amount"].apply(
            lambda x: convert_currency(x, "USD", selected_currency, exchange_rates)
        )
    else:
        df["display_amount"] = df["amount"]
    
    # Format with currency symbol
    df["Amount"] = df["display_amount"].apply(lambda x: f"{currency_symbol}{x:.2f}")
    # Create clean table
    display_df = df[["date", "Amount", "category", "note"]].rename(
        columns={"date": "Date", "category": "Category", "note": "Note"}
    )
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("💡 No expenses recorded yet. Add your first expense above!")
```

**Lines 232-290: Financial Summary**
```python
# Show summary only if both budget and expenses exist
if budget_data and not df.empty:
    st.header("💳 Financial Summary")
    
    # Calculate totals
    total_usd = df["amount"].sum()  # Sum all expenses in USD
    total_display = (
        convert_currency(total_usd, "USD", selected_currency, exchange_rates)
        if exchange_rates
        else total_usd
    )
    
    # Get budget in selected currency
    budget_amount, budget_currency = budget_data
    budget_display = (
        convert_currency(budget_amount, budget_currency, selected_currency, exchange_rates)
        if exchange_rates and budget_currency != selected_currency
        else budget_amount
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Show spending metric
        st.metric("Total Spent This Month", f"{currency_symbol}{total_display:.2f}")
        
        # Budget status with color coding
        remaining = budget_display - total_display
        if remaining < 0:
            st.error(f"🚨 Over budget by {currency_symbol}{abs(remaining):.2f}")
            progress = 1.0  # 100% if over budget
        else:
            st.success(f"✅ {currency_symbol}{remaining:.2f} remaining")
            progress = total_display / budget_display if budget_display > 0 else 0
        
        # Progress bar
        st.progress(min(progress, 1.0))
        st.caption(f"Budget: {currency_symbol}{budget_display:.2f}")
    
    with col2:
        # Category breakdown
        category_summary = df.groupby("category")["amount"].sum()
        # Convert to selected currency
        if exchange_rates and selected_currency != "USD":
            category_summary = category_summary.apply(
                lambda x: convert_currency(x, "USD", selected_currency, exchange_rates)
            )
        
        st.subheader("Spending by Category")
        # Show each category with percentage
        for cat, amount in category_summary.items():
            percentage = (amount / total_display * 100) if total_display > 0 else 0
            st.write(f"**{cat}**: {currency_symbol}{amount:.2f} ({percentage:.1f}%)")
    
    # Visual chart
    st.header("📈 Spending Visualization")
    st.bar_chart(category_summary)
```

### utils.py - Currency Utilities (Line by Line)

**Lines 1-2: Imports**
```python
import requests  # For making HTTP requests to currency API
import streamlit as st  # For displaying error messages
```

**Lines 4-35: Exchange Rate Fetching**
```python
def get_exchange_rates(base_currency="USD"):
    # Function to get current exchange rates from free API
    try:
        # Build API URL with base currency
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        # Make HTTP request with 5 second timeout
        response = requests.get(url, timeout=5)
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()  # Parse JSON response
            return data.get("rates", {})  # Return rates dictionary
        else:
            return None  # Return None if request failed
    except Exception as e:
        # Show error in Streamlit interface
        st.error(f"Error fetching exchange rates: {e}")
        return None
```

**Lines 37-70: Currency Conversion**
```python
def convert_currency(amount, from_currency, to_currency, rates):
    # Function to convert between currencies using rates
    
    # If no rates or same currency, return original
    if not rates or from_currency == to_currency:
        return amount
    
    try:
        # All conversions go through USD as base
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
            # Target is USD
            converted_amount = usd_amount
        
        return round(converted_amount, 2)  # Round to 2 decimals
    except:
        return amount  # Return original if conversion fails
```

**Lines 72-90: Currency Symbol Mapping**
```python
def get_currency_symbol(currency_code):
    # Function to get display symbol for currency
    
    # Dictionary mapping codes to symbols
    symbols = {
        "USD": "$",   # US Dollar
        "EUR": "€",   # Euro
        "GBP": "£",   # British Pound
        "NGN": "₦",   # Nigerian Naira
        "JPY": "¥",   # Japanese Yen
        "CAD": "C$",  # Canadian Dollar
        "AUD": "A$",  # Australian Dollar
    }
    # Return symbol or currency code if not found
    return symbols.get(currency_code, currency_code)
```

**Lines 92-100: Supported Currencies**
```python
def get_popular_currencies():
    # Function to return list of supported currencies
    return ["USD", "EUR", "GBP", "NGN", "JPY", "CAD", "AUD"]
```

## API Used 🌐

This app uses the **ExchangeRate-API** (free tier):
- No API key required for basic usage
- Updates exchange rates daily
- Supports 160+ currencies
- Fallback to USD if API fails
- API endpoint: `https://api.exchangerate-api.com/v4/latest/USD`

## Database Schema 🗄️

### expenses table
```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY,     -- Auto-incrementing ID
    date TEXT,                  -- Expense date (YYYY-MM-DD)
    amount REAL,                -- Amount in USD (base currency)
    category TEXT,              -- Expense category
    note TEXT                   -- Optional note
);
```

### budget table
```sql
CREATE TABLE budget (
    id INTEGER PRIMARY KEY,     -- Auto-incrementing ID
    month TEXT UNIQUE,          -- Month in YYYY-MM format
    amount REAL,                -- Budget amount
    currency TEXT               -- Currency code (USD, EUR, etc.)
);
```

## Customization Ideas 💡

**Beginner Level:**
- Add more expense categories
- Change the app colors/theme
- Add more chart types

**Intermediate Level:**
- Add expense editing/deletion
- Create monthly/yearly reports
- Add expense search functionality

**Advanced Level:**
- Add user authentication
- Create expense predictions
- Add receipt photo uploads

## Troubleshooting 🔧

**App won't start?**
- Check if Python is installed: `python --version`
- Install requirements: `pip install -r requirements.txt`

**Currency conversion not working?**
- Check internet connection
- App will use USD as fallback

**Database errors?**
- Delete `database.db` file and restart the app

## Learning Resources 📚

- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLite Tutorial](https://www.sqlitetutorial.net/)
- [Python Requests Library](https://requests.readthedocs.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## Contributing 🤝

This is a learning project! Feel free to:
- Add new features
- Fix bugs
- Improve documentation
- Share your improvements

## License 📄

This project is open source and available under the MIT License.

---

**Happy Budgeting! 🎉**

*Built with ❤️ for learning Python web development*