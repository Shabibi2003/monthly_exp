import sqlite3

def init_db():
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
    conn.close()

# Run the init_db function to create the database table
if __name__ == "__main__":
    init_db()
    print("Database initialized and table created successfully!")
