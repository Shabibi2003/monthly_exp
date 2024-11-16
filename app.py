import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

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

def delete_expense(expense_id):
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

def delete_all_expenses():
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses")  # Delete all rows in the expenses table
    conn.commit()
    conn.close()

def fetch_expenses():
    conn = init_connection()
    expenses_df = pd.read_sql_query("SELECT * FROM expenses", conn)
    conn.close()
    return expenses_df

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

# Button to delete all records in the database
if st.sidebar.button("Delete All Records"):
    delete_all_expenses()
    st.sidebar.success("All records have been deleted!")

# Display expenses
st.header("Expenses Overview")
expenses_df = fetch_expenses()

if not expenses_df.empty:
    st.dataframe(expenses_df)

    # Deleting a specific expense
    st.header("Delete a Specific Expense")
    selected_id = st.selectbox("Select Expense ID to Delete", expenses_df["id"])
    if st.button("Delete Selected Expense"):
        delete_expense(selected_id)
        st.success(f"Expense ID {selected_id} has been deleted!")
        st.experimental_rerun()

    # Display summary statistics
    st.header("Summary")
    total_expense = expenses_df["amount"].sum()
    st.write(f"Total Monthly Expense: ₹{total_expense}")

    # Display expenditure by category
    category_summary = expenses_df.groupby("category")["amount"].sum().reset_index()
    st.bar_chart(category_summary, x="category", y="amount")
    
    # Expenses over time graph
    st.header("Expenses Over Time")
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
    expenses_over_time = expenses_df.groupby('date')['amount'].sum().reset_index()

    # Plotting the expenses over time graph
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(expenses_over_time['date'], expenses_over_time['amount'], marker='o', color='tab:blue')
    ax.set_title("Expenses Over Time", fontsize=14)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Total Expenses", fontsize=12)
    ax.grid(True)
    st.pyplot(fig)
else:
    st.write("No expenses recorded yet.")
