import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import pytz
from dotenv import load_dotenv
import os

from dotenv import load_dotenv
import os

load_dotenv()  # This must be called before os.getenv

# --- Simple Login Section ---
def check_login():
    USERNAME = os.getenv("LOGIN_ID")
    PASSWORD = os.getenv("LOGIN_PASSWORD")
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if not st.session_state["logged_in"]:
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == USERNAME and password == PASSWORD:
                st.session_state["logged_in"] = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
        st.stop()  # Stop the app here if not logged in

check_login()

st.set_page_config(
    page_title="Monthly Expenditure",
    layout="wide",
    page_icon='📊',
    initial_sidebar_state="expanded"
)

# Essential CSS styling
st.markdown("""
    <style>
        .main-header {
            text-align: center;
            color: #2c3e50;
            padding: 20px;
            background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .red-line {
            border-top: 3px solid red;
            margin-top: 30px;
            margin-bottom: 30px;
        }
        .image-align {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            padding-bottom: 20px;
        }
        /* Removed input and select box visibility overrides */
        .stSelectbox div[role="option"]:hover {
            background-color: #007bff !important;
            color: white !important;
        }
        /* Metric cards in analytics */
        div[data-testid="metric-container"] {
            background-color: #2d2d2d;
            padding: 15px;
            border-radius: 10px;
            color: white !important;
            width: 100%;
        }
        div[data-testid="metric-container"] label,
        div[data-testid="metric-container"] div {
            color: white !important;
        }
        /* Tab styling */
        button[data-baseweb="tab"] {
            font-size: 20px !important;
            padding: 15px 30px !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            color: #ffffff !important;
            background-color: #007bff !important;
            margin-right: 10px !important;
        }
        button[data-baseweb="tab"]:hover {
            background-color: #0056b3 !important;
            transition: background-color 0.3s ease;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #0056b3 !important;
            border-bottom: 4px solid #ffcc00 !important;
        }
        /* Form Submit Button */
        div.stButton>button {
            background-color: #28a745;
            color: white;
            padding: 12px 30px;
            font-size: 18px;
            border-radius: 10px;
            transition: all 0.3s ease-in-out;
        }
        div.stButton>button:hover {
            background-color: #218838;
            transform: scale(1.05);
        }
    </style>
""", unsafe_allow_html=True)

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

def add_transaction(date_time, category, description, amount, transaction_type, sub_category, payment_method):
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute(""" 
        INSERT INTO transactions (date_time, category, description, amount, transaction_type, sub_category, payment_method)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (date_time, category, description, amount, transaction_type, sub_category, payment_method))
    conn.commit()
    conn.close()

def remove_transaction(transaction_id):
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = %s", (transaction_id,))
    conn.commit()
    conn.close()

def fetch_transactions():
    conn = init_connection()
    transactions_df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    return transactions_df

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

create_table()

# Main UI (single column, no photo)
st.markdown('<h1 class="main-header" style="margin-bottom:0;">Monthly Expenditure Tracker</h1>', unsafe_allow_html=True)

# Add gap between header and analytics boxes
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- Analytics Metrics (always visible, below header) ---
transactions_df = fetch_transactions()
if not transactions_df.empty:
    total_in = transactions_df[
        (transactions_df["transaction_type"] == "Cash In") &
        (transactions_df["sub_category"] != "Monthly Savings")
    ]["amount"].sum()
    total_out = transactions_df[transactions_df["transaction_type"] == "Cash Out"]["amount"].sum()
    balance = total_in - total_out
    monthly_savings = transactions_df[
        (transactions_df["transaction_type"] == "Cash In") &
        (transactions_df["sub_category"] == "Monthly Savings")
    ]["amount"].sum()
else:
    total_in = total_out = balance = monthly_savings = 0

st.markdown(f"""
<style>
.custom-metric-row {{
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
}}
.custom-metric-box {{
    flex: 1;
    background: #232323;
    border-radius: 8px;
    padding: 12px 5px 8px 5px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.10);
    border: 1px solid #444;
    color: white;
    text-align: center;
    min-width: 0;
}}
.custom-metric-label {{
    color: #bbb;
    font-size: 0.95em;
    margin-bottom: 4px;
    font-weight: 500;
}}
.custom-metric-value {{
    color: #fff;
    font-size: 1.2em;
    font-weight: bold;
}}
</style>
<div class="custom-metric-row">
    <div class="custom-metric-box">
        <div class="custom-metric-label">Total Income</div>
        <div class="custom-metric-value">₹{total_in:,.2f}</div>
    </div>
    <div class="custom-metric-box">
        <div class="custom-metric-label">Total Expenses</div>
        <div class="custom-metric-value">₹{total_out:,.2f}</div>
    </div>
    <div class="custom-metric-box">
        <div class="custom-metric-label">Balance</div>
        <div class="custom-metric-value">₹{balance:,.2f}</div>
    </div>
    <div class="custom-metric-box">
        <div class="custom-metric-label">Monthly Savings</div>
        <div class="custom-metric-value">₹{monthly_savings:,.2f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)

st.markdown("""
    <style>
        .tab-gap {
            margin-bottom: 70px;
        }
    </style>
    <div class="tab-gap"></div>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        .main-header {
            text-align: center;
            color: #2c3e50;
            padding: 20px;
            background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .red-line {
            border-top: 3px solid red;
            margin-top: 30px;
            margin-bottom: 30px;
        }
        .image-align {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            padding-bottom: 20px;
        }
        /* Removed input and select box visibility overrides */
        .stSelectbox div[role="option"]:hover {
            background-color: #007bff !important;
            color: white !important;
        }
        /* Metric cards in analytics */
        div[data-testid="metric-container"] {
            background-color: #2d2d2d;
            padding: 15px;
            border-radius: 10px;
            color: white !important;
            width: 100%;
        }
        div[data-testid="metric-container"] label,
        div[data-testid="metric-container"] div {
            color: white !important;
        }
        /* Tab styling */
        button[data-baseweb="tab"] {
            font-size: 20px !important;
            padding: 15px 30px !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            color: #ffffff !important;
            background-color: #007bff !important;
            margin-right: 10px !important;
        }
        button[data-baseweb="tab"]:hover {
            background-color: #0056b3 !important;
            transition: background-color 0.3s ease;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #0056b3 !important;
            border-bottom: 4px solid #ffcc00 !important;
        }
        /* Form Submit Button */
        div.stButton>button {
            background-color: #28a745;
            color: white;
            padding: 12px 30px;
            font-size: 18px;
            border-radius: 10px;
            transition: all 0.3s ease-in-out;
        }
        div.stButton>button:hover {
            background-color: #218838;
            transform: scale(1.05);
        }
    </style>
""", unsafe_allow_html=True)

# Add this line before using tab1, tab2, tab3
tab1, tab2, tab3 = st.tabs(["💰 Transactions", "📊 Analytics", "➕ Add Transaction"])

# Transactions Tab
with tab1:
    transactions_df = fetch_transactions()
    if not transactions_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            category_filter = st.multiselect("Filter by Category", transactions_df['category'].unique())
        with col2:
            type_filter = st.multiselect("Filter by Type", transactions_df['transaction_type'].unique())

        st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)
        filtered_df = transactions_df
        if category_filter:
            filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]
        if type_filter:
            filtered_df = filtered_df[filtered_df['transaction_type'].isin(type_filter)]

        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("No transactions recorded yet.")

st.markdown("<br>", unsafe_allow_html=True)

# Analytics Tab
with tab2:
    transactions_df = fetch_transactions()
    if not transactions_df.empty:
        total_in = transactions_df[
            (transactions_df["transaction_type"] == "Cash In") &
            (transactions_df["sub_category"] != "Monthly Savings")
        ]["amount"].sum()
        total_out = transactions_df[transactions_df["transaction_type"] == "Cash Out"]["amount"].sum()
        balance = total_in - total_out
        monthly_savings = transactions_df[
            (transactions_df["transaction_type"] == "Cash In") &
            (transactions_df["sub_category"] == "Monthly Savings")
        ]["amount"].sum()

        st.markdown(f"""
        <style>
        .custom-metric-row {{
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
        }}
        .custom-metric-box {{
            flex: 1;
            background: #232323;
            border-radius: 8px;
            padding: 12px 5px 8px 5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.10);
            border: 1px solid #444;
            color: white;
            text-align: center;
            min-width: 0;
        }}
        .custom-metric-label {{
            color: #bbb;
            font-size: 0.95em;
            margin-bottom: 4px;
            font-weight: 500;
        }}
        .custom-metric-value {{
            color: #fff;
            font-size: 1.2em;
            font-weight: bold;
        }}
        </style>
        <div class="custom-metric-row">
            <div class="custom-metric-box">
                <div class="custom-metric-label">Total Income</div>
                <div class="custom-metric-value">₹{total_in:,.2f}</div>
            </div>
            <div class="custom-metric-box">
                <div class="custom-metric-label">Total Expenses</div>
                <div class="custom-metric-value">₹{total_out:,.2f}</div>
            </div>
            <div class="custom-metric-box">
                <div class="custom-metric-label">Balance</div>
                <div class="custom-metric-value">₹{balance:,.2f}</div>
            </div>
            <div class="custom-metric-box">
                <div class="custom-metric-label">Monthly Savings</div>
                <div class="custom-metric-value">₹{monthly_savings:,.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        chart_df = transactions_df[
            (transactions_df["sub_category"] != "Monthly Savings") &
            (transactions_df["category"] != "Salary") &
            (transactions_df["transaction_type"] == "Cash Out")
        ]

        chart_type = st.selectbox("Select Chart Type", [
            "Category Distribution", 
            "Time Series", 
            "Payment Methods",
            "Daily Expenses",
            "Monthly Trend",
            "Category Comparison"
        ])
        
        if chart_type == "Category Distribution":
            fig = plt.figure(figsize=(6, 4))
            category_data = chart_df.groupby('category')['amount'].sum()
            plt.pie(category_data, labels=category_data.index, autopct='%1.1f%%')
            plt.title("Expenses by Category")
            plt.savefig("category_distribution.png")
            st.image("category_distribution.png")
            
        elif chart_type == "Time Series":
            fig = plt.figure(figsize=(6, 4))
            chart_df['date_time'] = pd.to_datetime(chart_df['date_time'])
            time_data = chart_df.groupby('date_time')['amount'].sum()
            plt.plot(time_data.index, time_data.values)
            plt.title("Time Series of Expenses")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig("time_series.png")
            st.image("time_series.png")
            
        elif chart_type == "Payment Methods":
            fig = plt.figure(figsize=(6, 4))
            payment_data = chart_df.groupby('payment_method')['amount'].sum()
            plt.bar(payment_data.index, payment_data.values)
            plt.title("Expenses by Payment Method")
            plt.savefig("payment_methods.png")
            st.image("payment_methods.png")
            
        elif chart_type == "Daily Expenses":
            fig = plt.figure(figsize=(10, 5))
            chart_df['date_time'] = pd.to_datetime(chart_df['date_time'])
            chart_df['day_of_week'] = chart_df['date_time'].dt.day_name()
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily_expenses = chart_df.groupby('day_of_week')['amount'].mean().reindex(day_order)
            plt.bar(daily_expenses.index, daily_expenses.values)
            plt.title("Average Daily Expenses")
            plt.xticks(rotation=45)
            plt.ylabel("Amount (₹)")
            plt.tight_layout()
            plt.savefig("daily_expenses.png")
            st.image("daily_expenses.png")
            
        elif chart_type == "Monthly Trend":
            fig = plt.figure(figsize=(10, 5))
            chart_df['month'] = chart_df['date_time'].dt.strftime('%Y-%m')
            monthly_expenses = chart_df.groupby('month')['amount'].sum()
            plt.plot(monthly_expenses.index, monthly_expenses.values, marker='o')
            plt.title("Monthly Expense Trend")
            plt.xticks(rotation=45)
            plt.ylabel("Total Amount (₹)")
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig("monthly_trend.png")
            st.image("monthly_trend.png")
            
        elif chart_type == "Category Comparison":
            fig = plt.figure(figsize=(10, 5))
            # First ensure date_time is datetime
            chart_df['date_time'] = pd.to_datetime(chart_df['date_time'])
            # Create month column before pivot
            chart_df['month'] = chart_df['date_time'].dt.strftime('%Y-%m')
            
            # Create pivot table with explicit month column
            category_monthly = pd.pivot_table(
                data=chart_df,
                values='amount',
                index='month',
                columns='category',
                aggfunc='sum',
                fill_value=0
            )
            
            # Plot the stacked bar chart
            category_monthly.plot(kind='bar', stacked=True)
            plt.title("Monthly Expenses by Category")
            plt.xlabel("Month")
            plt.ylabel("Amount (₹)")
            plt.legend(title="Categories", bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.savefig("category_comparison.png")
            st.image("category_comparison.png")
        
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Add Transaction Tab
with tab3:
    st.markdown('<div class="custom-form-width">', unsafe_allow_html=True)
    with st.form("transaction_form"):
        # First row: Date and Time
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            date = st.date_input("Date")
        with row1_col2:
            local_timezone = pytz.timezone("Asia/Kolkata")
            current_time = datetime.now(local_timezone).strftime('%H:%M:%S')
            time = st.text_input("Time", current_time)

        # Second row: Amount and Description
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            amount = st.number_input("Amount", min_value=0.0, step=0.01)
        with row2_col2:
            description = st.text_input("Description")

        # Place Transaction Type and Category side by side
        col5, col6 = st.columns(2)
        with col5:
            transaction_type = st.selectbox("Transaction Type", ["Cash Out", "Cash In"])
        with col6:
            category = st.selectbox("Category", ["Food", "Transport", "Utilities", "Salary", "Monthly Home Expenses", "Others"], disabled=False)

        payment_method = st.radio(
            "Payment Method",
            options=["💵 Cash", "💳 Online"],
            horizontal=True,
            key="payment_method_radio"
        )
        payment_method = "Cash" if payment_method == "💵 Cash" else "Online"
        submit = st.form_submit_button("Add Transaction")

        if submit:
            date_time = f"{date} {time}"
            add_transaction(date_time, category, description, amount, transaction_type, None, payment_method)
            st.success("Transaction added successfully!")
            st.session_state['rerun'] = True
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Reload"):
        st.rerun()

    # --- Monthly Saving Section ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h4 style="margin-top:30px;">Add Monthly Saving</h4>', unsafe_allow_html=True)
    with st.form("monthly_saving_form"):
        ms_date = st.date_input("Saving Date", key="ms_date")
        ms_local_timezone = pytz.timezone("Asia/Kolkata")
        ms_current_time = datetime.now(ms_local_timezone).strftime('%H:%M:%S')
        ms_time = st.text_input("Saving Time", ms_current_time, key="ms_time")
        ms_amount = st.number_input("Saving Amount", min_value=0.0, step=0.01, key="ms_amount")
        ms_payment_method = st.selectbox("Saving Payment Method", ["Cash", "Online"], key="ms_payment_method")
        ms_submit = st.form_submit_button("Add Monthly Saving")
        if ms_submit:
            ms_date_time = f"{ms_date} {ms_time}"
            add_transaction(ms_date_time, "Savings", "Monthly Saving", ms_amount, "Cash In", "Monthly Savings", ms_payment_method)
            st.success("Monthly saving added successfully!")
            st.session_state['rerun'] = True

st.markdown("<br>", unsafe_allow_html=True)

with st.expander("🗑️ Delete Transaction"):
    with st.form("delete_form"):
        transaction_id = st.number_input("Transaction ID to Delete", min_value=1, step=1)
        delete_submit = st.form_submit_button("Delete")
        if delete_submit:
            try:
                remove_transaction(transaction_id)
                st.success(f"Transaction {transaction_id} deleted successfully!")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Essential CSS styling
st.markdown("""
    <style>
        .main-header {
            text-align: center;
            color: #2c3e50;
            padding: 20px;
            background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .red-line {
            border-top: 3px solid red;
            margin-top: 30px;
            margin-bottom: 30px;
        }
        .image-align {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            padding-bottom: 20px;
        }
        /* Removed input and select box visibility overrides */
        .stSelectbox div[role="option"]:hover {
            background-color: #007bff !important;
            color: white !important;
        }
        /* Metric cards in analytics */
        div[data-testid="metric-container"] {
            background-color: #2d2d2d;
            padding: 15px;
            border-radius: 10px;
            color: white !important;
            width: 100%;
        }
        div[data-testid="metric-container"] label,
        div[data-testid="metric-container"] div {
            color: white !important;
        }
        /* Tab styling */
        button[data-baseweb="tab"] {
            font-size: 20px !important;
            padding: 15px 30px !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            color: #ffffff !important;
            background-color: #007bff !important;
            margin-right: 10px !important;
        }
        button[data-baseweb="tab"]:hover {
            background-color: #0056b3 !important;
            transition: background-color 0.3s ease;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #0056b3 !important;
            border-bottom: 4px solid #ffcc00 !important;
        }
        /* Form Submit Button */
        div.stButton>button {
            background-color: #28a745;
            color: white;
            padding: 12px 30px;
            font-size: 18px;
            border-radius: 10px;
            transition: all 0.3s ease-in-out;
        }
        div.stButton>button:hover {
            background-color: #218838;
            transform: scale(1.05);
        }
    </style>
""", unsafe_allow_html=True)









