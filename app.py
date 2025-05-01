import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import pytz

st.set_page_config(
    page_title="Monthly Expenditure",
    layout="wide",
    page_icon = '📊',
    initial_sidebar_state="expanded"
)
# Custom CSS styling
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
        .card {
            padding: 40px;
            border-radius: 10px;
            background-color: #ffffff;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .metric-card {
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 5px solid #007bff;
        }
        .stButton>button {
            width: 100%;
            background-color: #007bff;
            color: white;
            border-radius: 5px;
        }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        /* Fix for input and select box text visibility */
        input, textarea, select {
            color: black !important;
            background-color: white !important;
        }
        .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
            color: black !important;
            background-color: white !important;
        }
        .stSelectbox div[data-baseweb="select"] * {
            color: black !important;
            background-color: white !important;
        }
        .stSelectbox div[role="option"] {
            color: black !important;
            background-color: white !important;
        }
        .stSelectbox div[role="option"]:hover {
            background-color: #007bff !important;
            color: white !important;
        }
        .stDataFrame {
            font-size: 16px !important;
            padding: 20px 0 !important;
        }
        div[data-testid="stExpander"] {
            padding: 30px !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 28px !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 16px !important;
        }
        /* Fix for metric cards in analytics */
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
        .metric-card {
            padding: 5px !important;
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
        /* Info/success message */
        .element-container .stAlert-success {
            background-color: #d4edda;
            border-left: 5px solid #28a745;
            font-size: 16px;
            border-radius: 8px;
        }
        .element-container .stAlert-info,
        .element-container .stAlert-error {
            font-size: 16px;
            border-radius: 8px;
        }
        .red-line {
            border-top: 3px solid red;
            margin-top: 30px;
            margin-bottom: 30px;
        }

    </style>
""", unsafe_allow_html=True)

# Add this CSS rule in the existing style section
st.markdown("""
    <style>
        /* Fix for select box text visibility */
        .stSelectbox div[data-baseweb="select"] > div {
            color: black !important;
            background-color: white !important;
        }
        .stSelectbox div[data-baseweb="select"] > div:hover {
            border-color: #007bff !important;
        }
        .stSelectbox div[role="listbox"] {
            background-color: white !important;
        }
        .stSelectbox div[role="option"] {
            color: black !important;
        }
        .stSelectbox div[role="option"]:hover {
            background-color: #007bff !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# Update the CSS styles
st.markdown("""
    <style>
        /* Fix for input and select box text visibility */
        .stTextInput>div>div>input {
            color: black !important;
            background-color: white !important;
        }
        .stNumberInput>div>div>input {
            color: black !important;
            background-color: white !important;
        }
        .stSelectbox>div>div {
            color: black !important;
            background-color: white !important;
        }
        
        /* Fix for metric cards in analytics */
        div[data-testid="metric-container"] {
            background-color: #2d2d2d;
            padding: 15px;
            border-radius: 10px;
            color: white !important;
            width: 100%;
        }
        
        div[data-testid="metric-container"] label {
            color: white !important;
        }
        
        div[data-testid="metric-container"] div {
            color: white !important;
        }
        
        .metric-card {
            padding: 5px !important;
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

# Function to remove a transaction by ID
def remove_transaction(transaction_id):
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = %s", (transaction_id,))
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

# Move the Lottie imports and functions here
import requests
from streamlit_lottie import st_lottie
import json

def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Main UI
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown('<h1 class="main-header" style="margin-bottom:0;">Monthly Expenditure Tracker</h1>', unsafe_allow_html=True)
with col2:
    st.markdown(
        """
        <style>
        .lottie-align {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            /* Remove or reduce top padding for better vertical alignment */
            padding-bottom: 20;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    try:
        lottie_money = load_lottie_url('https://assets2.lottiefiles.com/packages/lf20_5ngs2ksb.json')
        # Use the container to ensure the animation stays in the column
        with st.container():
            st.markdown('<div class="lottie-align">', unsafe_allow_html=True)
            st_lottie(lottie_money, height=100, key="header_money")
            st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div class="lottie-align">📊</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Define tabs first
tab1, tab2, tab3 = st.tabs(["💰 Transactions", "📊 Analytics", "➕ Add Transaction"])

st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)

# Add a gap below the tabs
st.markdown("""
    <style>
        .tab-gap {
            margin-bottom: 70px;
        }
    </style>
    <div class="tab-gap"></div>
""", unsafe_allow_html=True)

# Transactions Tab
with tab1:
    transactions_df = fetch_transactions()  # Fetch transactions each time the tab is rendered
    if not transactions_df.empty:
        # Add search and filter functionality
        search_term = st.text_input("🔍 Search transactions", "")
        col1, col2 = st.columns(2)
        with col1:
            category_filter = st.multiselect("Filter by Category", transactions_df['category'].unique())
        with col2:
            type_filter = st.multiselect("Filter by Type", transactions_df['transaction_type'].unique())

        # Add red line below search section
        st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)
        # Apply filters
        filtered_df = transactions_df
        if search_term:
            filtered_df = filtered_df[filtered_df['description'].str.contains(search_term, case=False)]
        if category_filter:
            filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]
        if type_filter:
            filtered_df = filtered_df[filtered_df['transaction_type'].isin(type_filter)]

        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("No transactions recorded yet.")
    st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)  # Add red line after search section

st.markdown("<br>", unsafe_allow_html=True)

# Analytics Tab
with tab2:
    transactions_df = fetch_transactions()  # Fetch transactions each time the tab is rendered
    if not transactions_df.empty:
        # Only include non-savings for balance and total_in
        total_in = transactions_df[
            (transactions_df["transaction_type"] == "Cash In") &
            (transactions_df["sub_category"] != "Monthly Savings")
        ]["amount"].sum()
        total_out = transactions_df[transactions_df["transaction_type"] == "Cash Out"]["amount"].sum()
        balance = total_in - total_out
        # Monthly savings is always shown separately
        monthly_savings = transactions_df[
            (transactions_df["transaction_type"] == "Cash In") &
            (transactions_df["sub_category"] == "Monthly Savings")
        ]["amount"].sum()

        st.markdown(f"""
        <style>
        .custom-metric-row {{
            display: flex;
            gap: 12px; /* Reduced gap */
            margin-bottom: 20px; /* Reduced margin */
        }}
        .custom-metric-box {{
            flex: 1;
            background: #232323;
            border-radius: 8px; /* Slightly smaller radius */
            padding: 12px 5px 8px 5px; /* Reduced padding */
            box-shadow: 0 2px 8px rgba(0,0,0,0.10); /* Slightly lighter shadow */
            border: 1px solid #444; /* Thinner border */
            color: white;
            text-align: center;
            min-width: 0;
        }}
        .custom-metric-label {{
            color: #bbb;
            font-size: 0.95em; /* Smaller label font */
            margin-bottom: 4px;
            font-weight: 500;
        }}
        .custom-metric-value {{
            color: #fff;
            font-size: 1.2em; /* Smaller value font */
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
        
        # st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        chart_type = st.selectbox("Select Chart Type", ["Category Distribution", "Time Series", "Payment Methods"])
        
        if chart_type == "Category Distribution":
            fig = plt.figure(figsize=(6, 4))  # Reduced size
            category_data = transactions_df.groupby('category')['amount'].sum()
            plt.pie(category_data, labels=category_data.index, autopct='%1.1f%%')
            plt.title("Expenses by Category")
            plt.savefig("category_distribution.png")  # Save as image
            st.image("category_distribution.png")  # Display image
            
        elif chart_type == "Time Series":
            fig = plt.figure(figsize=(6, 4))  # Reduced size
            transactions_df['date_time'] = pd.to_datetime(transactions_df['date_time'])
            time_data = transactions_df.groupby('date_time')['amount'].sum()
            plt.plot(time_data.index, time_data.values)
            plt.title("Time Series of Transactions")
            plt.savefig("time_series.png")  # Save as image
            st.image("time_series.png")  # Display image
            
        elif chart_type == "Payment Methods":
            fig = plt.figure(figsize=(6, 4))  # Reduced size
            payment_data = transactions_df.groupby('payment_method')['amount'].sum()
            plt.bar(payment_data.index, payment_data.values)
            plt.title("Expenses by Payment Method")
            plt.savefig("payment_methods.png")  # Save as image
            st.image("payment_methods.png")  # Display image
        
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# Add Transaction Tab
with tab3:
    # st.markdown('<div class="card">', unsafe_allow_html=True)
    with st.form("transaction_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date")
            local_timezone = pytz.timezone("Asia/Kolkata")
            current_time = datetime.now(local_timezone).strftime('%H:%M:%S')
            time = st.text_input("Time", current_time)
            transaction_type = st.selectbox("Transaction Type", ["Cash In", "Cash Out"])
            category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Utilities", "Salary", "Investment", "Others"], disabled=False)
        
        with col2:
            description = st.text_input("Description")
            amount = st.number_input("Amount", min_value=0.0, step=0.01)
            
        payment_method = st.selectbox("Payment Method", ["Cash", "Online"])
        submit = st.form_submit_button("Add Transaction")

        if submit:
            date_time = f"{date} {time}"
            add_transaction(date_time, category, description, amount, transaction_type, None, payment_method)  # Removed sub_category
            st.success("Transaction added successfully!")
            st.session_state['rerun'] = True  # Set rerun flag
    st.markdown('</div>', unsafe_allow_html=True)

    # Add a reload button
    if st.button("Reload"):
        st.rerun()  # Rerun the script to refresh the data

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
            # Store as Cash In, sub_category="Monthly Savings"
            add_transaction(ms_date_time, "Savings", "Monthly Saving", ms_amount, "Cash In", "Monthly Savings", ms_payment_method)
            st.success("Monthly saving added successfully!")
            st.session_state['rerun'] = True

st.markdown("<br>", unsafe_allow_html=True)

# Delete transaction functionality
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

# Remove .metric-card and .card from your CSS if you only want the Streamlit metrics as boxes
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
        /* Style Streamlit metric boxes */
        div[data-testid="metric-container"] {
            background-color: #232323;
            border-radius: 12px;
            padding: 30px 10px 20px 10px;
            margin-bottom: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.12);
            border: 2px solid #444;
            color: white !important;
        }
        div[data-testid="metric-container"] label,
        div[data-testid="metric-container"] div {
            color: white !important;
        }
        div[data-testid="metric-container"] p {
            color: white !important;
        }
        div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
            color: #bbb !important;
        }
        div[data-testid="metric-container"] [data-testid="stMetricValue"] {
            color: #fff !important;
            font-size: 2em !important;
        }
        /* ... keep your other CSS ... */
    </style>
""", unsafe_allow_html=True)
