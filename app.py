import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Initialize the Database Connection
def init_connection():
    return sqlite3.connect('expenses.db')

# Ensure table exists and has required columns
def check_table_structure():
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(expenses);")
    columns = cursor.fetchall()
    conn.close()
    return columns

def add_transaction_column():
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE expenses ADD COLUMN transaction_type TEXT;")
    conn.commit()
    conn.close()

# Ensure the 'transaction_type' column exists
columns = check_table_structure()
if not any(col[1] == "transaction_type" for col in columns):
    add_transaction_column()

# Function to add transaction to the database
def add_transaction(date, category, description, amount, transaction_type):
    print(f"Adding transaction: {date}, {category}, {description}, {amount}, {transaction_type}")
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expenses (date, category, description, amount, transaction_type)
        VALUES (?, ?, ?, ?, ?)
    """, (date, category, description, amount, transaction_type))
    conn.commit()  # Commit the changes
    conn.close()   # Close the connection
    print("Transaction added to database successfully.")

# Function to fetch all transactions
def fetch_transactions():
    conn = init_connection()
    transactions_df = pd.read_sql_query("SELECT * FROM expenses", conn)  # Fetch data
    conn.close()
    return transactions_df

# Streamlit app title
st.title("Monthly Expenditure Tracker")

# Sidebar form for new transaction (Cash In / Cash Out)
st.sidebar.header("Add New Transaction")
with st.sidebar.form("transaction_form"):
    date = st.date_input("Date")
    category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Utilities", "Salary", "Investment", "Others"])
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    transaction_type = st.selectbox("Transaction Type", ["Cash In", "Cash Out"])
    submit = st.form_submit_button("Add Transaction")

    # Add data to the database
    if submit:
        add_transaction(date, category, description, amount, transaction_type)
        st.sidebar.success(f"{transaction_type} added successfully!")

# Button to delete all records in the database
if st.sidebar.button("Delete All Records"):
    delete_all_expenses()
    st.sidebar.success("All records have been deleted!")

# Display transactions
st.header("Transactions Overview")
transactions_df = fetch_transactions()

if not transactions_df.empty:
    st.dataframe(transactions_df)

    # Deleting a specific transaction
    st.header("Delete a Specific Transaction")
    selected_id = st.selectbox("Select Transaction ID to Delete", transactions_df["id"])

    if st.button("Delete Selected Transaction"):
        delete_expense(selected_id)
        st.success(f"Transaction ID {selected_id} has been deleted!")

        # Fetch updated data and refresh UI
        transactions_df = fetch_transactions()
        st.dataframe(transactions_df)

    # Display summary statistics
    st.header("Summary")
    if "transaction_type" in transactions_df.columns:
        cash_in = transactions_df[transactions_df["transaction_type"] == "Cash In"]["amount"].sum()
        cash_out = transactions_df[transactions_df["transaction_type"] == "Cash Out"]["amount"].sum()
        remaining_balance = cash_in - cash_out

        st.write(f"Total Cash In: ₹{cash_in}")
        st.write(f"Total Cash Out: ₹{cash_out}")
        st.write(f"Remaining Balance: ₹{remaining_balance}")
    else:
        st.error("Transaction type column is missing.")

    # Display expenditure by category
    category_summary = transactions_df.groupby("category")["amount"].sum().reset_index()
    st.bar_chart(category_summary, x="category", y="amount")
    
    # Transactions over time graph
    st.header("Transactions Over Time")
    transactions_df['date'] = pd.to_datetime(transactions_df['date'])
    transactions_over_time = transactions_df.groupby('date')['amount'].sum().reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(transactions_over_time['date'], transactions_over_time['amount'], marker='o', color='tab:blue')
    ax.set_title("Transactions Over Time", fontsize=14)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Amount", fontsize=12)
    ax.grid(True)
    st.pyplot(fig)
else:
    st.write("No transactions recorded yet.")
