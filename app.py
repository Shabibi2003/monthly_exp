import mysql.connector
import streamlit as st
import pandas as pd

# Function to connect to MySQL database
def init_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",  # Replace with your MySQL host (e.g., 'localhost' for local or the cloud server's address)
            user="user1",  # Replace with your MySQL username
            password="Usman@9876",  # Replace with your MySQL password
            database="expenses"  # Replace with your MySQL database name
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        raise  # Re-raise the error after logging it

# Function to initialize the database (create table if not exists)
def init_db():
    conn = init_connection()
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            category VARCHAR(100) NOT NULL,
            description TEXT,
            amount FLOAT NOT NULL,
            transaction_type VARCHAR(20) NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Function to add a transaction
def add_transaction(date, category, description, amount, transaction_type):
    conn = init_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO expenses (date, category, description, amount, transaction_type)
        VALUES (%s, %s, %s, %s, %s)
    """, (date, category, description, amount, transaction_type))

    conn.commit()
    conn.close()
    st.success(f"{transaction_type} added successfully!")

# Function to fetch transactions from MySQL
def fetch_transactions():
    conn = init_connection()
    query = "SELECT * FROM expenses"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Example usage within Streamlit
def app():
    # Initialize the database (create table)
    init_db()

    # Streamlit UI
    st.title("Monthly Expenditure Tracker")

    st.sidebar.header("Add New Transaction")
    with st.sidebar.form("transaction_form"):
        date = st.date_input("Date")
        category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Utilities", "Salary", "Investment", "Others"])
        description = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.0, step=0.01)
        transaction_type = st.selectbox("Transaction Type", ["Cash In", "Cash Out"])
        submit = st.form_submit_button("Add Transaction")

        if submit:
            add_transaction(date, category, description, amount, transaction_type)

    # Display transactions
    st.header("Transactions Overview")
    transactions_df = fetch_transactions()

    if not transactions_df.empty:
        st.dataframe(transactions_df)

    # Deleting a specific transaction
    st.header("Delete a Specific Transaction")
    if not transactions_df.empty:
        selected_id = st.selectbox("Select Transaction ID to Delete", transactions_df["id"])
        if st.button("Delete Selected Transaction"):
            delete_expense(selected_id)
            st.success(f"Transaction ID {selected_id} has been deleted!")
            transactions_df = fetch_transactions()  # Refresh the transactions
            st.dataframe(transactions_df)
    else:
        st.write("No transactions recorded yet.")

# Function to delete an expense (not yet implemented in the original code)
def delete_expense(transaction_id):
    conn = init_connection()
    cursor = conn.cursor()

    # Delete the selected transaction from the database
    cursor.execute("DELETE FROM expenses WHERE id = %s", (transaction_id,))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    app()
