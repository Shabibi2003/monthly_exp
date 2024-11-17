import mysql.connector
from mysql.connector import Error

# Establishing the connection
def create_connection():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host="127.0.0.1",  # MySQL server address (localhost in this case)
            user="root",        # Your MySQL username
            password="Usman@9876",  # Your MySQL password
            database="expenses_db"  # The database you want to connect to
        )
        
        if connection.is_connected():
            print("Successfully connected to the database")
            return connection
    except Error as err:
        print(f"Error: {err}")
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
        print("Table created successfully or already exists.")
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
        print(f"Data inserted: {name}, {age}")
        connection.close()

# Fetch data from table
def fetch_data():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}")
        connection.close()

# Example usage
if __name__ == "__main__":
    create_table()  # Create table
    insert_data("John Doe", 30)  # Insert a record
    insert_data('Yousf',21)
    insert_data('Yousf',21)
    fetch_data()  # Fetch and display all records
