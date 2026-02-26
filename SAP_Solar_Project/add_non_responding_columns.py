import sqlite3
import os

# Path to the database
db_path = os.path.join(os.path.dirname(__file__), 'database.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Starting non-responding customer migration...")

cursor.execute("PRAGMA table_info(crm)")
columns = [column[1] for column in cursor.fetchall()]

if 'is_non_responding' not in columns:
    cursor.execute("ALTER TABLE crm ADD COLUMN is_non_responding BOOLEAN DEFAULT 0")
    print("✓ Added is_non_responding column")

if 'marked_non_responding_at' not in columns:
    cursor.execute("ALTER TABLE crm ADD COLUMN marked_non_responding_at DATETIME")
    print("✓ Added marked_non_responding_at column")

cursor.execute("UPDATE crm SET is_non_responding = 0 WHERE is_non_responding IS NULL")

conn.commit()
conn.close()

print("Non-responding customer migration completed successfully!")
