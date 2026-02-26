import sqlite3
import os
from datetime import datetime

# Path to the database
db_path = os.path.join(os.path.dirname(__file__), 'database.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Starting remark_date migration...")

# Check if remark_date column exists in crm_remark table
cursor.execute("PRAGMA table_info(crm_remark)")
columns = [column[1] for column in cursor.fetchall()]

if 'remark_date' not in columns:
    try:
        # Add remark_date column
        cursor.execute("ALTER TABLE crm_remark ADD COLUMN remark_date DATE")
        print("✓ Added remark_date column to crm_remark table")
        
        # Set existing remarks to use the date from created_at
        cursor.execute("""
            UPDATE crm_remark 
            SET remark_date = DATE(created_at)
            WHERE remark_date IS NULL
        """)
        print(f"✓ Updated {cursor.rowcount} existing remarks with dates from created_at")
        
        # Commit changes
        conn.commit()
        print("✓ Migration completed successfully!")
        
    except Exception as e:
        print(f"✗ Error during migration: {e}")
        conn.rollback()
        conn.close()
        exit(1)
else:
    print("✓ remark_date column already exists")

conn.close()
print("Done!")
