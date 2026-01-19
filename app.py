import sqlite3
import streamlit as st
import pandas as pd
from utils import (
    get_exchange_rates,
    convert_currency,
    get_currency_symbol,
    get_popular_currencies,
)

# Initialize database with two tables: expenses and budget
conn = sqlite3.connect("database.db")
cursor = conn.cursor()
# Create expenses table to store all spending records
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
# Create budget table to store monthly budget settings
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS budget (
        id INTEGER PRIMARY KEY,
        month TEXT UNIQUE,
        amount REAL,
        currency TEXT
    )
    """
)
conn.commit()
conn.close()

# Configure Streamlit page settings
st.set_page_config(page_title="Smart Budget App", page_icon="💰")
st.title("💰 Smart Budget App")
st.markdown("*Set your budget first, then track expenses with multi-currency support*")

# Sidebar for currency selection
st.sidebar.header("Currency Settings")
currencies = get_popular_currencies()  # Get list of supported currencies
selected_currency = st.sidebar.selectbox(
    "Select Currency",
    currencies,
    index=0,  # Default to first currency (USD)
    help="Choose your preferred currency for display",
)

# Cache exchange rates for 1 hour to improve performance
@st.cache_data(ttl=3600)
def fetch_rates():
    return get_exchange_rates()  # Fetch from API

exchange_rates = fetch_rates()  # Get current exchange rates
currency_symbol = get_currency_symbol(selected_currency)  # Get symbol for display

# Show connection status in sidebar
if exchange_rates:
    st.sidebar.success(f"✅ Exchange rates updated")
else:
    st.sidebar.warning("⚠️ Using offline mode (USD only)")
    selected_currency = "USD"  # Fallback to USD
    currency_symbol = "$"

# Step 1: Budget Setup (must be done first)
st.header("🎯 Step 1: Set Your Monthly Budget")

# Get current month for budget tracking
import datetime
current_month = datetime.datetime.now().strftime("%Y-%m")

# Check if budget exists for current month
conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute("SELECT amount, currency FROM budget WHERE month = ?", (current_month,))
budget_data = cursor.fetchone()
conn.close()

if budget_data:
    # Display existing budget
    budget_amount, budget_currency = budget_data
    # Convert budget to selected currency if needed
    display_budget = (
        convert_currency(budget_amount, budget_currency, selected_currency, exchange_rates)
        if exchange_rates and budget_currency != selected_currency
        else budget_amount
    )
    st.success(f"✅ Monthly budget set: {currency_symbol}{display_budget:.2f}")
    
    # Option to update budget
    if st.button("Update Budget"):
        st.session_state.update_budget = True
else:
    st.warning("⚠️ Please set your monthly budget first before adding expenses")
    st.session_state.update_budget = True

# Budget input form
if st.session_state.get('update_budget', False):
    with st.form("budget_form"):
        st.subheader("Set Monthly Budget")
        budget_input = st.number_input(
            f"Budget Amount ({currency_symbol})",
            min_value=0.0,
            step=10.0,
            help=f"Enter your monthly budget in {selected_currency}"
        )
        
        if st.form_submit_button("💾 Save Budget", type="primary"):
            if budget_input > 0:
                # Store budget in database
                conn = sqlite3.connect("database.db")
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO budget (month, amount, currency) VALUES (?, ?, ?)",
                    (current_month, budget_input, selected_currency)
                )
                conn.commit()
                conn.close()
                st.success(f"✅ Budget of {currency_symbol}{budget_input} saved!")
                st.session_state.update_budget = False
                st.rerun()
            else:
                st.error("Please enter a valid budget amount")

# Step 2: Add Expenses (only if budget is set)
if budget_data or st.session_state.get('update_budget', False) == False:
    st.header("➕ Step 2: Add Your Expenses")
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Date input for expense
        date = st.date_input("Date", help="Select the date of your expense")
        # Amount input with currency symbol
        amount = st.number_input(
            f"Amount ({currency_symbol})",
            min_value=0.0,
            step=0.01,
            help=f"Enter amount in {selected_currency}",
        )
    
    with col2:
        # Category selection dropdown
        category = st.selectbox(
            "Category",
            ["Food", "Transport", "Rent", "Bills", "Entertainment", "Shopping", "Healthcare", "Other"],
            help="Choose the expense category",
        )
        # Optional note field
        note = st.text_input("Note (Optional)", help="Add any additional details")
    
    # Add expense button
    if st.button("➕ Add Expense", type="primary"):
        if amount > 0:
            # Convert amount to USD for consistent storage
            usd_amount = (
                convert_currency(amount, selected_currency, "USD", exchange_rates)
                if exchange_rates
                else amount
            )
            
            # Insert expense into database
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO expenses (date, amount, category, note) VALUES (?, ?, ?, ?)",
                (date, usd_amount, category, note),
            )
            conn.commit()
            conn.close()
            st.success(f"✅ Expense of {currency_symbol}{amount} added successfully!")
            st.rerun()  # Refresh page to show updated data
        else:
            st.error("⚠️ Please enter a valid amount greater than 0")

# Step 3: View Expenses and Budget Status
st.header("📊 Step 3: Your Expenses & Budget Status")

# Load all expenses from database
conn = sqlite3.connect("database.db")
df = pd.read_sql("SELECT * FROM expenses ORDER BY date DESC", conn)
conn.close()

if not df.empty:
    # Convert USD amounts to selected currency for display
    if exchange_rates and selected_currency != "USD":
        df["display_amount"] = df["amount"].apply(
            lambda x: convert_currency(x, "USD", selected_currency, exchange_rates)
        )
    else:
        df["display_amount"] = df["amount"]
    
    # Format amounts with currency symbol
    df["Amount"] = df["display_amount"].apply(lambda x: f"{currency_symbol}{x:.2f}")
    # Create clean display table
    display_df = df[["date", "Amount", "category", "note"]].rename(
        columns={"date": "Date", "category": "Category", "note": "Note"}
    )
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("💡 No expenses recorded yet. Add your first expense above!")

# Financial Summary (only show if both budget and expenses exist)
if budget_data and not df.empty:
    st.header("💳 Financial Summary")
    
    # Calculate total spending in selected currency
    total_usd = df["amount"].sum()
    total_display = (
        convert_currency(total_usd, "USD", selected_currency, exchange_rates)
        if exchange_rates
        else total_usd
    )
    
    # Get budget amount in selected currency
    budget_amount, budget_currency = budget_data
    budget_display = (
        convert_currency(budget_amount, budget_currency, selected_currency, exchange_rates)
        if exchange_rates and budget_currency != selected_currency
        else budget_amount
    )
    
    # Create two columns for metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Show total spent
        st.metric("Total Spent This Month", f"{currency_symbol}{total_display:.2f}")
        
        # Budget status with color coding
        remaining = budget_display - total_display
        if remaining < 0:
            st.error(f"🚨 Over budget by {currency_symbol}{abs(remaining):.2f}")
            progress = 1.0  # 100% if over budget
        else:
            st.success(f"✅ {currency_symbol}{remaining:.2f} remaining")
            progress = total_display / budget_display if budget_display > 0 else 0
        
        # Progress bar showing budget usage
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
        # Display each category with amount
        for cat, amount in category_summary.items():
            percentage = (amount / total_display * 100) if total_display > 0 else 0
            st.write(f"**{cat}**: {currency_symbol}{amount:.2f} ({percentage:.1f}%)")
    
    # Visual chart
    st.header("📈 Spending Visualization")
    st.bar_chart(category_summary)

elif budget_data and df.empty:
    st.info("💡 Budget is set! Now add some expenses to see your financial summary.")
elif not budget_data:
    st.info("💡 Set your budget first to see financial tracking features.")
