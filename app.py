import streamlit as st
import mysql.connector
from mysql.connector import Error

# Using the website URL of your MySQL server
db_url = https://monthlyexp-o67nvcwqw6u3sfazx88fsc.streamlit.app"  # Replace this with your actual MySQL server URL

# Function to establish the MySQL connection
def create_connection():
    try:
        # Connect to the remote MySQL server (use your username and password)
        connection = mysql.connector.connect(
            host=db_url,         # MySQL server address (Website URL or domain)
            user="project",        # Your MySQL username
            password="Usman@9876",    # Your MySQL password
            database="expenses"     # The database you want to use
        )
        
        if connection.is_connected():
            return connection
    except Error as err:
        st.error(f"Error: {err}")
        return None

# Create table if it doesn't exist
def create_table():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                age INT
            )
        ''')
        connection.commit()
        connection.close()

# Insert data into table
def insert_data(name, age):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute(''' 
            INSERT INTO users (name, age)
            VALUES (%s, %s)
        ''', (name, age))
        connection.commit()
        connection.close()

# Fetch data from table
def fetch_data():
    connection = create_connection()
    data = []
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        for row in rows:
            data.append({"ID": row[0], "Name": row[1], "Age": row[2]})
        connection.close()
    return data

# Streamlit UI
st.title("MySQL Data Insertion and Display")

# Create table if it doesn't exist
create_table()

# User input for name and age
st.subheader("Insert Data")
name = st.text_input("Name")
age = st.number_input("Age", min_value=1, max_value=120)

if st.button("Insert Data"):
    if name and age:
        insert_data(name, age)
        st.success(f"Data inserted: {name}, {age}")
    else:
        st.warning("Please fill in both fields.")

# Display the data from the database
st.subheader("Database Records")
data = fetch_data()

if data:
    st.write(data)
else:
    st.warning("No data available.")
