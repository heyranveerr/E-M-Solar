import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), 'database.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if is_seen column already exists
    cursor.execute("PRAGMA table_info(crm_reminder)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'is_seen' not in columns:
        # Add the is_seen column
        cursor.execute('''
            ALTER TABLE crm_reminder ADD COLUMN is_seen BOOLEAN NOT NULL DEFAULT 0
        ''')
        conn.commit()
        print("Successfully added is_seen column to crm_reminder table")
    else:
        print("is_seen column already exists")
    
    # Show table structure
    cursor.execute("PRAGMA table_info(crm_reminder)")
    columns = cursor.fetchall()
    print("\nUpdated table structure:")
    for col in columns:
        print(f"  {col[1]} {col[2]}")

except sqlite3.Error as e:
    print(f"Database error: {e}")
    conn.rollback()
finally:
    conn.close()
