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
# st.markdown("""
#     <style>
#         .main-header {
#             text-align: center;
#             color: #2c3e50;
#             padding: 40px;
#             background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);
#             border-radius: 15px;
#             margin-bottom: 50px;
#             font-size: 2.8em;
#             box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
#         }
#         .card {
#             padding: 40px 20px;
#             background: none;
#             box-shadow: none;
#             margin: 0;
#             border: none;
#         }
#         .metric-card {
#             text-align: center;
#             padding: 35px;
#             background: #2d2d2d;
#             border-radius: 12px;
#             border-left: 6px solid #007bff;
#             box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
#             margin: 15px 0;
#             color: white;
#         }
#         .chart-container {
#             padding: 40px 20px;
#             background: none;
#             border: none;
#             margin: 30px 0;
#             color: white;
#         }
#         .stTextInput>div>div>input,
#         .stSelectbox>div>div,
#         .stNumberInput>div>div>input {
#             padding: 15px !important;
#             font-size: 16px !important;
#         }
#         .stDataFrame {
#             font-size: 16px !important;
#             padding: 20px 0 !important;
#         }
#         div[data-testid="stExpander"] {
#             padding: 30px !important;
#         }
#         div[data-testid="stMetricValue"] {
#             font-size: 28px !important;
#         }
#         div[data-testid="stMetricLabel"] {
#             font-size: 16px !important;
#         }

#         /* === NEW ADDITIONS BELOW === */

#         /* Larger, stylized tab buttons */
#         button[data-baseweb="tab"] {
#             font-size: 20px !important;
#             padding: 15px 30px !important;
#             font-weight: 600 !important;
#             border-radius: 10px !important;
#             color: #ffffff !important;
#             background-color: #007bff !important;
#             margin-right: 10px !important;
#         }
#         button[data-baseweb="tab"]:hover {
#             background-color: #0056b3 !important;
#             transition: background-color 0.3s ease;
#         }
#         button[data-baseweb="tab"][aria-selected="true"] {
#             background-color: #0056b3 !important;
#             border-bottom: 4px solid #ffcc00 !important;
#         }

#         /* Form Submit Button */
#         div.stButton>button {
#             background-color: #28a745;
#             color: white;
#             padding: 12px 30px;
#             font-size: 18px;
#             border-radius: 10px;
#             transition: all 0.3s ease-in-out;
#         }
#         div.stButton>button:hover {
#             background-color: #218838;
#             transform: scale(1.05);
#         }

#         /* Info/success message */
#         .element-container .stAlert-success {
#             background-color: #d4edda;
#             border-left: 5px solid #28a745;
#             font-size: 16px;
#             border-radius: 8px;
#         }
#         .element-container .stAlert-info,
#         .element-container .stAlert-error {
#             font-size: 16px;
#             border-radius: 8px;
#         }
#     </style>
# """, unsafe_allow_html=True)

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
            padding: 40px;  /* Increased padding for larger size */
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

        .stTextInput>div>div>input,
        .stSelectbox>div>div,
        .stNumberInput>div>div>input {
            padding: 15px !important;
            font-size: 16px !important;
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

        /* === NEW ADDITIONS BELOW === */

        /* Larger, stylized tab buttons */
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
    st.markdown('<h1 class="main-header">Monthly Expenditure Tracker</h1>', unsafe_allow_html=True)
with col2:
    try:
        lottie_money = load_lottie_url('https://assets2.lottiefiles.com/packages/lf20_5ngs2ksb.json')
        st_lottie(lottie_money, height=150, key="header_money")
    except:
        st.markdown("📊", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Define tabs first
tab1, tab2, tab3 = st.tabs(["💰 Transactions", "📊 Analytics", "➕ Add Transaction"])

# Then use the tabs
# In tab1, replace the animation section with just the content
with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    transactions_df = fetch_transactions()  # Fetch transactions each time the tab is rendered
    if not transactions_df.empty:
        # Add search and filter functionality
        search_term = st.text_input("🔍 Search transactions", "")
        col1, col2 = st.columns(2)
        with col1:
            category_filter = st.multiselect("Filter by Category", transactions_df['category'].unique())
        with col2:
            type_filter = st.multiselect("Filter by Type", transactions_df['transaction_type'].unique())
    
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
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="red-line"></div>', unsafe_allow_html=True)  # Add red line after search section

st.markdown("<br>", unsafe_allow_html=True)

with tab2:
    transactions_df = fetch_transactions()  # Fetch transactions each time the tab is rendered
    if not transactions_df.empty:
        col1, col2, col3, col4 = st.columns(4)  # Add a new column for monthly savings
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            # Exclude monthly savings from total income
            total_in = transactions_df[(transactions_df["transaction_type"] == "Cash In") & (transactions_df["sub_category"] != "Monthly Savings")]["amount"].sum()
            st.metric("Total Income", f"₹{total_in:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            total_out = transactions_df[transactions_df["transaction_type"] == "Cash Out"]["amount"].sum()
            st.metric("Total Expenses", f"₹{total_out:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            # Calculate balance without monthly savings
            balance = total_in - total_out
            st.metric("Balance", f"₹{balance:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            # Display monthly savings separately
            monthly_savings = transactions_df[(transactions_df["transaction_type"] == "Cash In") & (transactions_df["sub_category"] == "Monthly Savings")]["amount"].sum()
            st.metric("Monthly Savings", f"₹{monthly_savings:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

        # Interactive charts
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        chart_type = st.selectbox("Select Chart Type", ["Category Distribution", "Time Series", "Payment Methods"])
        
        # Filter out monthly savings from charts
        chart_df = transactions_df[transactions_df['sub_category'] != "Monthly Savings"]
        
        if chart_type == "Category Distribution":
            fig = plt.figure(figsize=(10, 6))
            category_data = chart_df.groupby('category')['amount'].sum()
            plt.pie(category_data, labels=category_data.index, autopct='%1.1f%%')
            plt.title("Expenses by Category")
            plt.savefig("category_distribution.png")
            st.image("category_distribution.png")
            
        elif chart_type == "Time Series":
            fig = plt.figure(figsize=(10, 6))
            chart_df['date_time'] = pd.to_datetime(chart_df['date_time'])
            time_data = chart_df.groupby('date_time')['amount'].sum()
            plt.plot(time_data.index, time_data.values)
            plt.title("Time Series of Transactions")
            plt.savefig("time_series.png")
            st.image("time_series.png")
            
        elif chart_type == "Payment Methods":
            fig = plt.figure(figsize=(10, 6))
            payment_data = chart_df.groupby('payment_method')['amount'].sum()
            plt.bar(payment_data.index, payment_data.values)
            plt.title("Expenses by Payment Method")
            plt.savefig("payment_methods.png")
            st.image("payment_methods.png")
        
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
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
            st.balloons()  # Add confetti effect
            st.session_state['rerun'] = True

        # Remove this block as it's causing the error
        # if savings_submit:
        #     savings_date_time = f"{savings_date} {current_time}"
        #     add_transaction(savings_date_time, "Savings", "Monthly Savings", savings_amount, "Cash In", "Monthly Savings", "Online")
        #     st.success("Monthly savings added successfully!")
        #     st.balloons()
        #     st.session_state['rerun'] = True
        st.markdown('</div>', unsafe_allow_html=True)

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
