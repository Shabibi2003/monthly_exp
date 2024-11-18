import mysql.connector
import streamlit as st

# Function to establish the MySQL connection
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
            port=4000,  # TiDB Cloud port
            user="nVBqARTHPX1yFUJ.root",
            password="L9Rs0LXsGYRYZyIE",
            database="fortune500",
            ssl_ca="ca-cert.pem"  # Path to the SSL certificate
        )
        if connection.is_connected():
            return connection
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None

# Insert data into the database
def insert_data(name, age):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (name, age) VALUES (%s, %s)", (name, age))
        connection.commit()
        connection.close()
        st.success(f"Data inserted: {name}, {age}")

# Fetch data from the database
def fetch_data():
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        data = cursor.fetchall()
        connection.close()
        return data

# Streamlit UI
st.title("TiDB Cloud with Streamlit")

# Insert data section
st.subheader("Insert Data")
name = st.text_input("Name")
age = st.number_input("Age", min_value=1, max_value=120)
if st.button("Insert"):
    if name and age:
        insert_data(name, age)
    else:
        st.warning("Please provide both name and age.")

# # Display data section
# st.subheader("Database Records")
# data = fetch_data()
# if data:
#     st.write(data)
# else:
#     st.warning("No data found.")
