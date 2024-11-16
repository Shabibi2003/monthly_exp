import sqlite3

def init_db():
    try:
        # Connect to the database file 'expenses.db'
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()

        # Create a table to store expenses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                amount REAL NOT NULL
            )
        ''')

        # Save changes and close the connection
        conn.commit()
        print("Database initialized and table created successfully!")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the connection
        if conn:
            conn.close()

# Run the init_db function to create the database table
if __name__ == "__main__":
    init_db()
