import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import pytz

# Function to establish the MySQL (TiDB) connection
def init_connection():
    return mysql.connector.connect(
        host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",  # TiDB Cloud host
        port=4000,  # TiDB Cloud port
        user="nVBqARTHPX1yFUJ.root",  # Your TiDB Cloud username
        password="L9Rs0LXsGYRYZyIE",  # Your TiDB Cloud password
        database="fortune500",  # Your TiDB Cloud database name
        ssl_ca="ca-cert.pem"  # Path to the SSL certificate
    )

def add_transaction(date_time, category, description, amount, transaction_type):
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute(""" 
        INSERT INTO transactions (date_time, category, description, amount, transaction_type)
        VALUES (%s, %s, %s, %s, %s)
    """, (date_time, category, description, amount, transaction_type))
    conn.commit()
    conn.close()

def delete_expense(transaction_id):
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = %s", (transaction_id,))
    conn.commit()
    conn.close()

def delete_all_expenses():
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")  # Delete all rows in the transactions table
    conn.commit()
    conn.close()

def fetch_transactions():
    conn = init_connection()
    transactions_df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    return transactions_df

# Ensure table exists with a combined date_time column
def create_table():
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date_time DATETIME,
            category VARCHAR(100),
            description VARCHAR(255),
            amount DECIMAL(10, 2),
            transaction_type VARCHAR(50)
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
    
    # Get the current time in the local timezone (India Standard Time)
    local_timezone = pytz.timezone("Asia/Kolkata")  # Adjust the timezone as needed
    current_time = datetime.now(local_timezone).strftime('%H:%M:%S')  # Current time in HH:MM:SS format
    
    # Time input field with default as current time
    time = st.text_input("Time", current_time)  # Display the current time in the input box
    category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Utilities", "Salary", "Investment", "Others"])
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    transaction_type = st.selectbox("Transaction Type", ["Cash In", "Cash Out", "Online", "Cash"])  # Added "Online" and "Cash"
    submit = st.form_submit_button("Add Transaction")

    # Add data to the database
    if submit:
        # Combine date and time into a single datetime string
        date_time = f"{date} {time}"
        add_transaction(date_time, category, description, amount, transaction_type)
        st.sidebar.success(f"{transaction_type} added successfully at {date_time}!")

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
    
    # Cash In, Cash Out, Online, and Cash calculation
    cash_in = transactions_df[transactions_df["transaction_type"] == "Cash In"]["amount"].sum()
    cash_out = transactions_df[transactions_df["transaction_type"] == "Cash Out"]["amount"].sum()
    online = transactions_df[transactions_df["transaction_type"] == "Online"]["amount"].sum()
    cash = transactions_df[transactions_df["transaction_type"] == "Cash"]["amount"].sum()
    remaining_balance = cash_in - cash_out + online - cash

    st.write(f"Total Cash In: ₹{cash_in}")
    st.write(f"Total Cash Out: ₹{cash_out}")
    st.write(f"Total Online Transactions: ₹{online}")
    st.write(f"Total Cash Transactions: ₹{cash}")
    st.write(f"Remaining Balance: ₹{remaining_balance}")

    # Display expenditure by category
    category_summary = transactions_df.groupby("category")["amount"].sum().reset_index()
    st.bar_chart(category_summary, x="category", y="amount")
    
    # Transactions over time graph
    st.header("Transactions Over Time")
    transactions_df['date_time'] = pd.to_datetime(transactions_df['date_time'])
    transactions_over_time = transactions_df.groupby('date_time')['amount'].sum().reset_index()

    # Plotting the transactions over time graph
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(transactions_over_time['date_time'], transactions_over_time['amount'], marker='o', color='tab:blue')
    ax.set_title("Transactions Over Time", fontsize=14)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Amount", fontsize=12)
    ax.grid(True)
    st.pyplot(fig)
else:
    st.write("No transactions recorded yet.")
