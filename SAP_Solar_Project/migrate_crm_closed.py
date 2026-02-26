import sqlite3
import os

# Path to the database
db_path = os.path.join(os.path.dirname(__file__), 'database.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if columns exist
cursor.execute("PRAGMA table_info(crm)")
columns = [column[1] for column in cursor.fetchall()]

# Add closed column if it doesn't exist
if 'closed' not in columns:
    cursor.execute("ALTER TABLE crm ADD COLUMN closed BOOLEAN DEFAULT 0")

# Commit changes and close connection
conn.commit()
conn.close()

print("CRM table migration completed successfully! Added 'closed' column.")
