import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import pytz
from dotenv import load_dotenv
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
        st.markdown("""
            <style>
            .login-container {
                max-width: 600px;
                margin: 60px auto;
                padding: 40px;
                background: linear-gradient(145deg, #2d2d2d, #353535);
                border-radius: 20px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.2);
                animation: fadeIn 0.5s ease-out;
            }
            .login-header {
                text-align: center;
                color: #fff;
                margin-bottom: 30px;
                font-size: 2em;
                font-weight: 600;
            }
            .login-icon {
                font-size: 50px;
                text-align: center;
                margin-bottom: 20px;
                color: #007bff;
            }
            .stTextInput input {
                background: rgba(255,255,255,0.05);
                border: 2px solid rgba(255,255,255,0.1);
                border-radius: 12px;
                padding: 12px 20px;
                color: white;
                font-size: 16px;
                transition: all 0.3s ease;
            }
            .stTextInput input:focus {
                border-color: #007bff;
                box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
                background: rgba(255,255,255,0.1);
            }
            .stButton>button {
                width: 100%;
                background: linear-gradient(45deg, #007bff, #00bfff);
                color: white;
                padding: 12px 0;
                font-size: 18px;
                font-weight: 600;
                border: none;
                border-radius: 12px;
                cursor: pointer;
                margin-top: 20px;
                transition: all 0.3s ease;
            }
            .stButton>button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,123,255,0.4);
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .error-message {
                background: rgba(255,59,48,0.1);
                color: #ff3b30;
                padding: 10px;
                border-radius: 8px;
                text-align: center;
                margin-top: 15px;
                animation: shake 0.5s ease-in-out;
            }
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-10px); }
                75% { transform: translateX(10px); }
            }
            </style>
            <div class="login-container">
                <div class="login-icon">🔐</div>
                <h1 class="login-header">Welcome Back Faisal </h1>
            </div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        # In the login section
        if st.button("Login", key="login_button"):
            if username == USERNAME and password == PASSWORD:
                st.session_state["logged_in"] = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.markdown("""
                    <div class="error-message">
                        ❌ Invalid username or password
                    </div>
                """, unsafe_allow_html=True)
        st.stop()

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
            padding: 25px;
            background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .custom-metric-box {
            flex: 1;
            background: linear-gradient(145deg, #2d2d2d, #353535);
            border-radius: 12px;
            padding: 15px 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            border: 1px solid #444;
            color: white;
            text-align: center;
            min-width: 0;
            transition: transform 0.2s ease;
        }
        .custom-metric-box:hover {
            transform: translateY(-3px);
        }
        .custom-metric-label {
            color: #e0e0e0;
            font-size: 1em;
            margin-bottom: 6px;
            font-weight: 500;
        }
        .custom-metric-value {
            color: #fff;
            font-size: 1.4em;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }
        /* Form styling */
        div.stTextInput input {
            border-radius: 8px;
            border: 1px solid #ddd;
            padding: 10px;
            transition: all 0.3s ease;
        }
        div.stTextInput input:focus {
            border-color: #007bff;
            box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
        }
        div.stSelectbox > div {
            border-radius: 8px;
        }
        /* Chart container styling */
        div.stImage {
            background: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            margin: 10px 0;
        }
        /* Tab styling improvements */
        button[data-baseweb="tab"] {
            font-size: 18px !important;
            padding: 12px 25px !important;
            font-weight: 500 !important;
            border-radius: 12px !important;
            background-color: rgba(0,123,255,0.8) !important;
            margin-right: 12px !important;
            transition: all 0.3s ease !important;
        }
        button[data-baseweb="tab"]:hover {
            background-color: rgba(0,86,179,0.9) !important;
            transform: translateY(-2px);
        }
        /* Form Submit Button enhancement */
        div.stButton>button {
            background: linear-gradient(145deg, #28a745, #218838);
            color: white;
            padding: 12px 35px;
            font-size: 16px;
            border-radius: 12px;
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        div.stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        }
        /* Login form styling */
        div[data-testid="stForm"] {
            background: rgba(255,255,255,0.05);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.1);
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
        INSERT INTO expenses (date_time, category, description, amount, transaction_type, sub_category, payment_method)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (date_time, category, description, amount, transaction_type, sub_category, payment_method))
    conn.commit()
    conn.close()

def remove_transaction(transaction_id):
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = %s", (transaction_id,))
    conn.commit()
    conn.close()

def fetch_transactions():
    conn = init_connection()
    transactions_df = pd.read_sql_query("SELECT * FROM expenses", conn)
    conn.close()
    return transactions_df

def create_table():
    conn = init_connection()
    cursor = conn.cursor()
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS expenses (
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

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Add About button in the top right corner
if st.button("ℹ️ About", key="about_button", help="Learn how to use the app"):
    # Clear the current UI
    st.empty()
    
    # Add title and description
    st.title("📊 Welcome to Monthly Expenditure Tracker!")
    st.write("This application helps you manage and track your monthly expenses efficiently. Here's how to use it:")
    
    # Key Features section
    st.header("🔑 Key Features")
    st.markdown("""
    * Track both income and expenses
    * Categorize transactions
    * Monitor monthly savings
    * View detailed analytics
    * Export transaction data
    """)
    
    # How to Use section
    st.header("📝 How to Use")
    
    # Add Transactions section
    st.subheader("1. Add Transactions (➕ Add Transaction tab)")
    st.markdown("""
    * Select transaction date and time
    * Choose transaction type (Cash In/Out)
    * Select category and sub-category
    * Enter amount and description
    * Choose payment method
    """)
    
    # View Transactions section
    st.subheader("2. View Transactions (💰 Transactions tab)")
    st.markdown("""
    * Search transactions using the search box
    * Filter by category, type, or payment method
    * Select date range to view specific periods
    * Export transactions to CSV
    """)
    
    # Analytics section
    st.subheader("3. Analytics (📊 Analytics tab)")
    st.markdown("""
    * View total income and expenses
    * Track current balance
    * Monitor monthly savings
    * Analyze spending patterns
    """)
    
    # Tips section
    st.header("💡 Tips")
    st.markdown("""
    * Regularly update your transactions for accurate tracking
    * Use categories consistently for better analysis
    * Export data periodically for backup
    * Monitor your savings goals through the analytics
    """)
    st.header("Latest Updates regarding this Application will be display here")
    st.markdown("No Updates yet")
    # Add back button
    if st.button("Back to Dashboard", key="back_button"):
        st.rerun()
    st.markdown("<br><br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)


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
            margin-bottom: 40px;
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
        
        # Enhanced filters
        col1, col2, col3 = st.columns(3)
        with col1:
            category_filter = st.multiselect("Filter by Category", transactions_df['category'].unique())
        with col2:
            type_filter = st.multiselect("Filter by Type", transactions_df['transaction_type'].unique())
        with col3:
            payment_filter = st.multiselect("Filter by Payment Method", transactions_df['payment_method'].unique())
        
        # Date range filter
        date_range = st.date_input(
            "Select Date Range",
            value=(transactions_df['date_time'].min().date(), transactions_df['date_time'].max().date()),
            key="transaction_date_range"
        )
        
        st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)
        
        # Apply filters
        filtered_df = transactions_df.copy()
        
        
        # Apply category filter
        if category_filter:
            filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]
        
        # Apply type filter
        if type_filter:
            filtered_df = filtered_df[filtered_df['transaction_type'].isin(type_filter)]
            
        # Apply payment method filter
        if payment_filter:
            filtered_df = filtered_df[filtered_df['payment_method'].isin(payment_filter)]
            
        # Apply date filter
        mask = (filtered_df['date_time'].dt.date >= date_range[0]) & (filtered_df['date_time'].dt.date <= date_range[1])
        filtered_df = filtered_df[mask]
        
        # Show results count
        st.markdown(f"<p style='color: #666;'>Showing {len(filtered_df)} transactions</p>", unsafe_allow_html=True)
        
        # Enhanced transaction table
        if not filtered_df.empty:
            # Format the dataframe
            display_df = filtered_df.copy()
            display_df['date_time'] = display_df['date_time'].dt.strftime('%Y-%m-%d %H:%M')
            display_df['amount'] = display_df['amount'].apply(lambda x: f"₹{x:,.2f}")
            
            st.dataframe(
                display_df,
                use_container_width=True,
                column_config={
                    "date_time": "Date & Time",
                    "category": "Category",
                    "description": "Description",
                    "amount": "Amount",
                    "transaction_type": "Type",
                    "sub_category": "Sub-Category",
                    "payment_method": "Payment Method"
                }
            )
        else:
            st.info("No transactions match your filters.")
        
        # Export functionality
        if st.button("Export to CSV"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="transactions.csv",
                mime="text/csv"
            )
    else:
        st.info("No transactions recorded yet.")

    # In the transactions tab
    if st.button("Reload", key="reload_button"):
        st.rerun()

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

        # Enhanced chart selection
        col1, col2 = st.columns(2)
        with col1:
            chart_type = st.selectbox("Select Chart Type", [
                "Category Distribution", 
                "Time Series", 
                "Payment Methods",
                "Daily Expenses",
                "Monthly Trend",
                "Category Comparison",
                "Budget vs Actual",  # New chart type
                "Savings Progress",  # New chart type
                "Expense Forecast"   # New chart type
            ])
        
        with col2:
            # Add time range filter
            date_range = st.date_input(
                "Select Date Range",
                value=(transactions_df['date_time'].min().date(), transactions_df['date_time'].max().date()),
                key="date_range"
            )
        
        # Filter data based on date range
        mask = (transactions_df['date_time'].dt.date >= date_range[0]) & (transactions_df['date_time'].dt.date <= date_range[1])
        filtered_df = transactions_df[mask]
        
        # Add summary metrics for selected period
        period_expenses = filtered_df[filtered_df['transaction_type'] == 'Cash Out']['amount'].sum()
        period_income = filtered_df[
            (filtered_df['transaction_type'] == 'Cash In') & 
            (filtered_df['sub_category'] != 'Monthly Savings')
        ]['amount'].sum()
        
        st.markdown(f"""
        <div class="period-summary" style="margin: 20px 0; padding: 15px; background: #2d2d2d; border-radius: 10px;">
            <h3 style="color: white; margin-bottom: 10px;">Selected Period Summary</h3>
            <div style="display: flex; gap: 20px;">
                <div style="flex: 1; text-align: center;">
                    <div style="color: #4CAF50; font-size: 1.2em;">Income</div>
                    <div style="color: white; font-size: 1.4em;">₹{period_income:,.2f}</div>
                </div>
                <div style="flex: 1; text-align: center;">
                    <div style="color: #f44336; font-size: 1.2em;">Expenses</div>
                    <div style="color: white; font-size: 1.4em;">₹{period_expenses:,.2f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
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



# adding comment to push the code









