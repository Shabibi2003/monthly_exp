import streamlit as st
import sqlite3
import pandas as pd

# Initialize the Database Connection
def init_connection():
    return sqlite3.connect('expenses.db')
def add_expense(date, category, description, amount):
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
                   (date, category, description, amount))
    conn.commit()
    conn.close()

# Streamlit app title
st.title("Monthly Expenditure Tracker")

# Sidebar form for new expense
st.sidebar.header("Add New Expense")
with st.sidebar.form("expense_form"):
    date = st.date_input("Date")
    category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Utilities", "Others"])
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    submit = st.form_submit_button("Add Expense")

    # Add data to the database
    if submit:
        add_expense(date, category, description, amount)
        st.sidebar.success("Expense added successfully!")

def fetch_expenses():
    conn = init_connection()
    expenses_df = pd.read_sql_query("SELECT * FROM expenses", conn)
    conn.close()
    return expenses_df

# Display expenses
st.header("Expenses Overview")
expenses_df = fetch_expenses()
st.dataframe(expenses_df)

# Display summary statistics
st.header("Summary")
if not expenses_df.empty:
    total_expense = expenses_df["amount"].sum()
    st.write(f"Total Monthly Expense: ₹{total_expense}")

    # Display expenditure by category
    category_summary = expenses_df.groupby("category")["amount"].sum().reset_index()
    st.bar_chart(category_summary, x="category", y="amount")
