import sqlite3
import os
from datetime import datetime

# Path to the database
db_path = os.path.join(os.path.dirname(__file__), 'database.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Starting CRM restructure migration...")

# 1. Create the crm_remark table
try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crm_remark (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crm_id INTEGER NOT NULL,
            remark TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(100),
            FOREIGN KEY (crm_id) REFERENCES crm(id) ON DELETE CASCADE
        )
    """)
    print("✓ Created crm_remark table")
except Exception as e:
    print(f"✗ Error creating crm_remark table: {e}")

# 2. Check existing CRM table structure
cursor.execute("PRAGMA table_info(crm)")
columns = {column[1]: column for column in cursor.fetchall()}
print(f"Current CRM columns: {list(columns.keys())}")

# 3. Migrate existing remark data to crm_remark table (if remark column exists)
if 'remark' in columns:
    try:
        cursor.execute("""
            INSERT INTO crm_remark (crm_id, remark, created_at, created_by)
            SELECT id, remark, created_at, employee_name
            FROM crm
            WHERE remark IS NOT NULL AND remark != ''
        """)
        print(f"✓ Migrated {cursor.rowcount} remarks to crm_remark table")
    except Exception as e:
        print(f"✗ Error migrating remarks: {e}")

# 4. Add updated_at column if it doesn't exist
if 'updated_at' not in columns:
    try:
        cursor.execute("ALTER TABLE crm ADD COLUMN updated_at DATETIME")
        # Set initial value to created_at for existing records
        cursor.execute("UPDATE crm SET updated_at = created_at WHERE updated_at IS NULL")
        print("✓ Added updated_at column to crm table")
    except Exception as e:
        print(f"✗ Error adding updated_at column: {e}")

# 5. Create a new CRM table without the old columns
# Since SQLite doesn't support DROP COLUMN easily, we need to recreate the table
try:
    # Get all current data (only from original entries to avoid duplicates)
    print("Backing up CRM data...")
    if 'is_original' in columns:
        cursor.execute("SELECT id, employee_name, customer_name, date, description, price, status, ivrm_number, created_at FROM crm WHERE is_original = 1 OR is_original IS NULL")
    else:
        cursor.execute("SELECT id, employee_name, customer_name, date, description, price, status, ivrm_number, created_at FROM crm")
    
    backup_data = cursor.fetchall()
    print(f"✓ Backed up {len(backup_data)} CRM entries")
    
    # Drop the old table
    cursor.execute("DROP TABLE IF EXISTS crm")
    print("✓ Dropped old crm table")
    
    # Create new table with correct structure
    cursor.execute("""
        CREATE TABLE crm (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name VARCHAR(100) NOT NULL,
            customer_name VARCHAR(100) NOT NULL,
            date DATE NOT NULL,
            description TEXT NOT NULL,
            price REAL DEFAULT 0.0,
            status VARCHAR(50) DEFAULT 'Pending',
            ivrm_number VARCHAR(100),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created new crm table with updated structure")
    
    # Restore data
    for row in backup_data:
        cursor.execute("""
            INSERT INTO crm (id, employee_name, customer_name, date, description, price, status, ivrm_number, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (*row, row[8]))  # Use created_at for updated_at initially
    print(f"✓ Restored {len(backup_data)} CRM entries")
    
except Exception as e:
    print(f"✗ Error restructuring crm table: {e}")
    conn.rollback()
    print("Rolling back changes...")
    conn.close()
    exit(1)

# Commit all changes
conn.commit()
conn.close()

print("\n✓ CRM restructure migration completed successfully!")
print("  - Removed parent-child versioning system")
print("  - Created separate crm_remark table")
print("  - Migrated existing remarks")
print("  - Added updated_at tracking")
