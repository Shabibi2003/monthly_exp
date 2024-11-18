import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import pytz

# Function to establish the MySQL (TiDB) connection
def init_connection():
    return mysql.connector.connect(
        host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
        port=4000,
        user="nVBqARTHPX1yFUJ.root",
        password="L9Rs0LXsGYRYZyIE",
        database="fortune500",
        ssl_ca="ca-cert.pem"
    )

# Function to add a transaction
def add_transaction(date_time, category, description, amount, transaction_type, sub_category, payment_method):
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute(""" 
        INSERT INTO transactions (date_time, category, description, amount, transaction_type, sub_category, payment_method)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (date_time, category, description, amount, transaction_type, sub_category, payment_method))
    conn.commit()
    conn.close()

# Function to fetch all transactions
def fetch_transactions():
    conn = init_connection()
    transactions_df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    return transactions_df

# Ensure table exists with updated schema
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
            transaction_type VARCHAR(50),
            sub_category VARCHAR(50),
            payment_method VARCHAR(50)
        )
    """)
    conn.commit()
    conn.close()

# Create table if not exists
create_table()

# Streamlit app title
st.title("Monthly Expenditure Tracker")

# Sidebar form for new transaction
st.sidebar.header("Add New Transaction")
with st.sidebar.form("transaction_form"):
    date = st.date_input("Date")
    
    # Get the current time in the local timezone
    local_timezone = pytz.timezone("Asia/Kolkata")
    current_time = datetime.now(local_timezone).strftime('%H:%M:%S')
    time = st.text_input("Time", current_time)
    
    category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Utilities", "Salary", "Investment", "Others"])
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    transaction_type = st.selectbox("Transaction Type", ["Cash In", "Cash Out"])
    
    # Subcategory selection based on transaction type
    if transaction_type == "Cash Out":
        sub_category = st.selectbox("Sub-Category", ["Monthly Expenses", "Other Expenses"])
    else:
        sub_category = st.selectbox("Sub-Category", ["Monthly Savings", "Other Savings"])
    
    payment_method = st.selectbox("Payment Method", ["Cash", "Online"])
    submit = st.form_submit_button("Add Transaction")

# Add transaction to database when form is submitted
if submit:
    date_time = f"{date} {time}"
    add_transaction(date_time, category, description, amount, transaction_type, sub_category, payment_method)
    st.sidebar.success(f"Transaction added successfully: {transaction_type} ({sub_category}) at {date_time}!")

# Fetch transactions
transactions_df = fetch_transactions()

# UI Layout with two columns
st.header("Overview")
col1, col2 = st.columns(2)

# Column 1: Overall data
with col1:
    st.subheader("Monthly Expendeture")
    if not transactions_df.empty:
        st.dataframe(transactions_df)
    else:
        st.write("No transactions recorded yet.")

# Column 2: Monthly Savings
with col2:
    st.subheader("Monthly Savings Summary")
    if not transactions_df.empty and "sub_category" in transactions_df.columns:
        monthly_savings = transactions_df[transactions_df["sub_category"] == "Monthly Savings"]
        total_monthly_savings = monthly_savings["amount"].sum()
        st.metric(label="Total Monthly Savings", value=f"₹{total_monthly_savings}")
    else:
        st.write("No savings data available.")

# Transactions Over Time
if not transactions_df.empty:
    st.header("Transactions Over Time")
    transactions_df['date_time'] = pd.to_datetime(transactions_df['date_time'])
    transactions_over_time = transactions_df.groupby('date_time')['amount'].sum().reset_index()

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(transactions_over_time['date_time'], transactions_over_time['amount'], marker='o', color='tab:blue')
    ax.set_title("Transactions Over Time", fontsize=14)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Amount", fontsize=12)
    ax.grid(True)
    st.pyplot(fig)

# Summary Statistics
if not transactions_df.empty:
    st.header("Summary")
    cash_in = transactions_df[transactions_df["transaction_type"] == "Cash In"]["amount"].sum()
    cash_out = transactions_df[transactions_df["transaction_type"] == "Cash Out"]["amount"].sum()
    online = transactions_df[transactions_df["payment_method"] == "Online"]["amount"].sum()
    cash = transactions_df[transactions_df["payment_method"] == "Cash"]["amount"].sum()
    remaining_balance = cash_in - cash_out

    st.write(f"Total Cash In: ₹{cash_in}")
    st.write(f"Total Cash Out: ₹{cash_out}")
    st.write(f"Total Online Transactions: ₹{online}")
    st.write(f"Total Cash Transactions: ₹{cash}")
    st.write(f"Remaining Balance: ₹{remaining_balance}")

    # Expenditure by category
    st.header("Category-wise Expenditure and Savings")
    category_summary = transactions_df.groupby(["category", "sub_category"])["amount"].sum().reset_index()
    st.bar_chart(category_summary, x="category", y="amount", color="sub_category")
