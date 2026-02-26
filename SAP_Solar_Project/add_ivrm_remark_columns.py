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

# Add ivrm_number column if it doesn't exist
if 'ivrm_number' not in columns:
    cursor.execute("ALTER TABLE crm ADD COLUMN ivrm_number VARCHAR(100)")
    print("Added ivrm_number column to crm table")
else:
    print("ivrm_number column already exists")

# Add remark column if it doesn't exist
if 'remark' not in columns:
    cursor.execute("ALTER TABLE crm ADD COLUMN remark TEXT")
    print("Added remark column to crm table")
else:
    print("remark column already exists")

# Commit changes and close connection
conn.commit()
conn.close()

print("CRM table migration completed successfully!")
