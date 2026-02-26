import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), 'database.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Create the crm_reminder table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crm_reminder (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crm_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            reminder_datetime DATETIME NOT NULL,
            reminder_text TEXT NOT NULL,
            is_dismissed BOOLEAN NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (crm_id) REFERENCES crm (id),
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
    ''')
    
    conn.commit()
    print("Successfully created crm_reminder table")
    
    # Verify the table was created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crm_reminder'")
    result = cursor.fetchone()
    if result:
        print(f"Table 'crm_reminder' exists: {result[0]}")
        
        # Show table structure
        cursor.execute("PRAGMA table_info(crm_reminder)")
        columns = cursor.fetchall()
        print("\nTable structure:")
        for col in columns:
            print(f"  {col[1]} {col[2]}")
    else:
        print("Error: Table was not created")

except sqlite3.Error as e:
    print(f"Database error: {e}")
    conn.rollback()
finally:
    conn.close()
