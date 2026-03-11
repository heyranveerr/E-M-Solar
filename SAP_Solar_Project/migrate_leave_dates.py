#!/usr/bin/env python
"""
Migration script to update leave_requests table from leave_date to start_date and end_date.
This preserves existing leave records by using leave_date as both start_date and end_date.
"""

import sqlite3

def migrate_leave_dates():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        # Check if the old leave_date column still exists
        cursor.execute("PRAGMA table_info(leave_requests)")
        columns = {col[1] for col in cursor.fetchall()}
        
        if 'leave_date' in columns:
            print("✓ leave_date column exists, starting migration...")
            
            # Create a new temporary table with the correct schema
            cursor.execute("""
                CREATE TABLE leave_requests_new (
                    id INTEGER PRIMARY KEY,
                    employee_id INTEGER NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    subject VARCHAR(200) NOT NULL,
                    message TEXT NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(employee_id) REFERENCES user(id)
                )
            """)
            
            # Copy data from old table, using leave_date for both start_date and end_date
            cursor.execute("""
                INSERT INTO leave_requests_new (id, employee_id, start_date, end_date, subject, message, status, created_at, updated_at)
                SELECT id, employee_id, leave_date, leave_date, subject, message, status, created_at, updated_at
                FROM leave_requests
            """)
            
            # Drop the old table
            cursor.execute("DROP TABLE leave_requests")
            
            # Rename the new table
            cursor.execute("ALTER TABLE leave_requests_new RENAME TO leave_requests")
            
            conn.commit()
            print("✓ Migration completed successfully!")
            print("✓ All existing leave dates have been set as both start_date and end_date.")
        else:
            print("✓ Table already has start_date and end_date columns. No migration needed.")
            
    except Exception as e:
        print(f"✗ Error during migration: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    migrate_leave_dates()
