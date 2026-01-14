import sqlite3
import streamlit as st
import pandas as pd

st.title("Smart Budgeting App")

st.header("Add Expense")

date = st.date_input("Date")
amount = st.number_input("Amount", min_value=0.0)
category = st.selectbox("Category", ["Food", "Transport", "Rent", "Bills", "Other"])
note = st.text_input("Note")

if st.button("Add Expense"):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (date, amount, category, note) VALUES (?, ?, ?, ?)",
        (date, amount, category, note),
    )
    conn.commit()
    conn.close()
    st.success("Expense added!")


st.header("All Expenses")

conn = sqlite3.connect("database.db")
df = pd.read_sql("SELECT * FROM expenses", conn)
conn.close()

st.dataframe(df)


st.header("Spending Summary")

total_spent = df["amount"].sum()
st.write("Total Spent:", total_spent)

category_summary = df.groupby("category")["amount"].sum()
st.write(category_summary)


st.header("Spending Chart")
st.bar_chart(category_summary)

st.header("Budget Alert")

budget = st.number_input("Set Monthly Budget", min_value=0.0)

if total_spent > budget and budget > 0:
    st.warning("You have exceeded your budget!")
else:
    st.success("You are within budget")


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
