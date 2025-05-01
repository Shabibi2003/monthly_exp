import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import pytz

st.set_page_config(
    page_title="Monthly Expenditure",
    layout="wide",
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

# Main UI
st.markdown('<h1 class="main-header">Monthly Expenditure Tracker</h1>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Tabs for different sections
tab1, tab2, tab3 = st.tabs(["💰 Transactions", "📊 Analytics", "➕ Add Transaction"])

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    transactions_df = fetch_transactions()
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

st.markdown("<br>", unsafe_allow_html=True)

with tab2:
    if not transactions_df.empty:
        col1, col2, col3, col4 = st.columns(4)  # Add a new column for monthly savings
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            total_in = transactions_df[transactions_df["transaction_type"] == "Cash In"]["amount"].sum()
            st.metric("Total Income", f"₹{total_in:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            total_out = transactions_df[transactions_df["transaction_type"] == "Cash Out"]["amount"].sum()
            st.metric("Total Expenses", f"₹{total_out:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            balance = total_in - total_out  # Exclude monthly savings from balance calculation
            st.metric("Balance", f"₹{balance:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            monthly_savings = transactions_df[(transactions_df["transaction_type"] == "Cash In") & (transactions_df["sub_category"] == "Monthly Savings")]["amount"].sum()
            st.metric("Monthly Savings", f"₹{monthly_savings:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

        # Interactive charts
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        chart_type = st.selectbox("Select Chart Type", ["Category Distribution", "Time Series", "Payment Methods"])
        
        if chart_type == "Category Distribution":
            fig = plt.figure(figsize=(10, 6))
            category_data = transactions_df.groupby('category')['amount'].sum()
            plt.pie(category_data, labels=category_data.index, autopct='%1.1f%%')
            plt.title("Expenses by Category")
            st.pyplot(fig)
            
        elif chart_type == "Time Series":
            transactions_df['date_time'] = pd.to_datetime(transactions_df['date_time'])
            time_data = transactions_df.groupby('date_time')['amount'].sum()
            st.line_chart(time_data)
            
        elif chart_type == "Payment Methods":
            payment_data = transactions_df.groupby('payment_method')['amount'].sum()
            st.bar_chart(payment_data)
        
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
            st.session_state['rerun'] = True  # Set rerun flag
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # New section for adding monthly savings
    with st.expander("➕ Add Monthly Savings"):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.form("monthly_savings_form"):
            savings_date = st.date_input("Savings Date")
            savings_amount = st.number_input("Savings Amount", min_value=0.0, step=0.01)
            savings_submit = st.form_submit_button("Add Monthly Savings")

            if savings_submit:
                savings_date_time = f"{savings_date} {current_time}"
                add_transaction(savings_date_time, "Savings", "Monthly Savings", savings_amount, "Cash In", "Monthly Savings", "Online")
                st.success("Monthly savings added successfully!")
                st.session_state['rerun'] = True  # Set rerun flag
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
