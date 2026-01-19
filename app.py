import sqlite3
import streamlit as st
import pandas as pd
from utils import get_exchange_rates, convert_currency, get_currency_symbol, get_popular_currencies

# Initialize database and create table if it doesn't exist
# This creates a local SQLite database to store all expense data
conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        date TEXT,
        amount REAL,
        category TEXT,
        note TEXT
    )
    """
)
conn.commit()
conn.close()

# App configuration and title
st.set_page_config(page_title="Smart Budget App", page_icon="💰")
st.title("💰 Smart Budget App")
st.markdown("*Track your expenses with multi-currency support*")

# Currency selection sidebar
st.sidebar.header("Currency Settings")
currencies = get_popular_currencies()
selected_currency = st.sidebar.selectbox(
    "Select Currency", 
    currencies, 
    index=0,  # Default to USD
    help="Choose your preferred currency for display"
)

# Fetch exchange rates (cached for performance)
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_rates():
    return get_exchange_rates()

exchange_rates = fetch_rates()
currency_symbol = get_currency_symbol(selected_currency)

# Display currency status
if exchange_rates:
    st.sidebar.success(f"✅ Exchange rates updated")
else:
    st.sidebar.warning("⚠️ Using offline mode (USD only)")
    selected_currency = "USD"
    currency_symbol = "$"

# Section: Add new expense
# This section allows users to input their daily expenses
st.header("➕ Add New Expense")

# Create input columns for better layout
col1, col2 = st.columns(2)

with col1:
    date = st.date_input("Date", help="Select the date of your expense")
    amount = st.number_input(
        f"Amount ({currency_symbol})", 
        min_value=0.0, 
        step=0.01,
        help=f"Enter amount in {selected_currency}"
    )

with col2:
    category = st.selectbox(
        "Category", 
        ["Food", "Transport", "Rent", "Bills", "Entertainment", "Shopping", "Healthcare", "Other"],
        help="Choose the expense category"
    )
    note = st.text_input("Note (Optional)", help="Add any additional details")

if st.button("➕ Add Expense", type="primary"):
    if amount > 0:
        # Insert expense into database (always store in USD for consistency)
        usd_amount = convert_currency(amount, selected_currency, "USD", exchange_rates) if exchange_rates else amount
        
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (date, amount, category, note) VALUES (?, ?, ?, ?)",
            (date, usd_amount, category, note),
        )
        conn.commit()
        conn.close()
        st.success(f"✅ Expense of {currency_symbol}{amount} added successfully!")
        st.rerun()  # Refresh the app to show new data
    else:
        st.error("⚠️ Please enter a valid amount greater than 0")

# Section: Display all expenses
# Show expenses in selected currency with better formatting
st.header("📊 Your Expenses")
conn = sqlite3.connect("database.db")
df = pd.read_sql("SELECT * FROM expenses ORDER BY date DESC", conn)
conn.close()

if not df.empty:
    # Convert amounts to selected currency for display
    if exchange_rates and selected_currency != "USD":
        df['display_amount'] = df['amount'].apply(
            lambda x: convert_currency(x, "USD", selected_currency, exchange_rates)
        )
    else:
        df['display_amount'] = df['amount']
    
    # Format the display
    df['Amount'] = df['display_amount'].apply(lambda x: f"{currency_symbol}{x:.2f}")
    display_df = df[['date', 'Amount', 'category', 'note']].rename(columns={
        'date': 'Date', 'category': 'Category', 'note': 'Note'
    })
    st.dataframe(display_df, width='stretch')
else:
    st.info("No expenses recorded yet. Add your first expense above!")

# Section: Spending summary and budget tracking
if not df.empty:
    st.header("💳 Financial Summary")
    
    # Convert total to selected currency
    total_usd = df["amount"].sum()
    total_display = convert_currency(total_usd, "USD", selected_currency, exchange_rates) if exchange_rates else total_usd
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Spent", f"{currency_symbol}{total_display:.2f}")
        
        # Budget tracking
        budget = st.number_input(
            f"Monthly Budget ({currency_symbol})", 
            min_value=0.0, 
            step=10.0,
            help="Set your monthly spending limit"
        )
        
        if budget > 0:
            remaining = budget - total_display
            if remaining < 0:
                st.error(f"⚠️ Over budget by {currency_symbol}{abs(remaining):.2f}")
            else:
                st.success(f"✅ {currency_symbol}{remaining:.2f} remaining")
    
    with col2:
        # Category breakdown
        category_summary = df.groupby("category")["amount"].sum()
        if exchange_rates and selected_currency != "USD":
            category_summary = category_summary.apply(
                lambda x: convert_currency(x, "USD", selected_currency, exchange_rates)
            )
        
        st.subheader("By Category")
        for cat, amount in category_summary.items():
            st.write(f"**{cat}**: {currency_symbol}{amount:.2f}")
    
    # Visualization
    st.header("📈 Spending Chart")
    st.bar_chart(category_summary)
