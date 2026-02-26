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

# Add parent_id column if it doesn't exist
if 'parent_id' not in columns:
    cursor.execute("ALTER TABLE crm ADD COLUMN parent_id INTEGER REFERENCES crm(id)")

# Add is_original column if it doesn't exist
if 'is_original' not in columns:
    cursor.execute("ALTER TABLE crm ADD COLUMN is_original BOOLEAN DEFAULT 1")

# Add price column if it doesn't exist
if 'price' not in columns:
    cursor.execute("ALTER TABLE crm ADD COLUMN price REAL DEFAULT 0.0")

# Commit changes and close connection
conn.commit()
conn.close()

print("CRM table migration completed successfully!")
