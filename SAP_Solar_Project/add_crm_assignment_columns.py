import sqlite3
import os

# Path to the database
db_path = os.path.join(os.path.dirname(__file__), 'database.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Starting CRM assignment migration...")

cursor.execute("PRAGMA table_info(crm)")
columns = [column[1] for column in cursor.fetchall()]

if 'assigned_to_id' not in columns:
    cursor.execute("ALTER TABLE crm ADD COLUMN assigned_to_id INTEGER")
    print("✓ Added assigned_to_id column")

if 'accepted_at' not in columns:
    cursor.execute("ALTER TABLE crm ADD COLUMN accepted_at DATETIME")
    print("✓ Added accepted_at column")

if 'is_closed' not in columns:
    cursor.execute("ALTER TABLE crm ADD COLUMN is_closed BOOLEAN DEFAULT 0")
    print("✓ Added is_closed column")

if 'closed_at' not in columns:
    cursor.execute("ALTER TABLE crm ADD COLUMN closed_at DATETIME")
    print("✓ Added closed_at column")

cursor.execute("UPDATE crm SET is_closed = 0 WHERE is_closed IS NULL")

conn.commit()
conn.close()

print("CRM assignment migration completed successfully!")
