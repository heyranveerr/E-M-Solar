import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'database.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check integrity
cursor.execute("PRAGMA integrity_check;")
integrity = cursor.fetchone()
print("Integrity check:", integrity)

# Get table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# Check solar_project table
cursor.execute("PRAGMA table_info(material);")
columns = cursor.fetchall()
print("Material columns:", columns)

cursor.execute("SELECT * FROM material;")
materials = cursor.fetchall()
print("Materials:", materials)

conn.close()
