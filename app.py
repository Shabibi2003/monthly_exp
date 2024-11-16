import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

def init_db():
    # Connect to the database file 'expenses.db'
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    # Create a table to store expenses
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            transaction_type TEXT NOT NULL
        )
    ''')

    # Save changes and close the connection
    conn.commit()
    conn.close()

# Run the init_db function to create the database table
if __name__ == "__main__":
    init_db()
    print("Database initialized and table created successfully!")

# Initialize the Database Connection
def init_connection():
    return sqlite3.connect('expenses.db')

def add_transaction(date, category, description, amount, transaction_type):
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expenses (date, category, description, amount, transaction_type)
        VALUES (?, ?, ?, ?, ?)
    """, (date, category, description, amount, transaction_type))
    conn.commit()  # Commit the changes
    conn.close()   # Close the connection

def delete_expense(transaction_id):
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (transaction_id,))
    conn.commit()
    conn.close()

def delete_all_expenses():
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses")  # Delete all rows in the expenses table
    conn.commit()
    conn.close()

def fetch_transactions():
    conn = init_connection()
    transactions_df = pd.read_sql_query("SELECT * FROM expenses", conn)  # Corrected to 'expenses' table
    conn.close()
    return transactions_df

# Ensure table exists
def create_table():
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            description TEXT,
            amount REAL,
            transaction_type TEXT
        )
    """)
    conn.commit()
    conn.close()

# Create table if not exists
create_table()

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
        st.experimental_rerun()  # Refresh the page after adding a transaction

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

    # Trigger deletion only when a valid ID is selected
    if st.button("Delete Selected Transaction"):
        delete_expense(selected_id)
        st.success(f"Transaction ID {selected_id} has been deleted!")

        # Fetch updated data and refresh UI
        transactions_df = fetch_transactions()
        st.dataframe(transactions_df)

    # Display summary statistics
    st.header("Summary")
    
    # Check if 'transaction_type' exists in DataFrame columns
    if "transaction_type" in transactions_df.columns:
        # Cash In and Cash Out calculation
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

    # Plotting the transactions over time graph
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(transactions_over_time['date'], transactions_over_time['amount'], marker='o', color='tab:blue')
    ax.set_title("Transactions Over Time", fontsize=14)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Amount", fontsize=12)
    ax.grid(True)
    st.pyplot(fig)
else:
    st.write("No transactions recorded yet.")
