#!/usr/bin/env python3
"""
Create payroll and leave management tables, plus supporting columns.
"""

import sqlite3
from pathlib import Path


def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return any(row[1] == column_name for row in cursor.fetchall())


def table_exists(cursor, table_name):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    return cursor.fetchone() is not None


def run():
    db_path = Path(__file__).parent / 'database.db'
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        if not column_exists(cursor, 'user', 'employee_id'):
            cursor.execute("ALTER TABLE user ADD COLUMN employee_id VARCHAR(50)")
        if not column_exists(cursor, 'user', 'email'):
            cursor.execute("ALTER TABLE user ADD COLUMN email VARCHAR(150)")
        if not column_exists(cursor, 'user', 'role'):
            cursor.execute("ALTER TABLE user ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'employee'")

        cursor.execute("UPDATE user SET role='admin' WHERE username='admin'")
        cursor.execute("UPDATE user SET role='employee' WHERE role IS NULL OR role = ''")

        if not column_exists(cursor, 'attendance', 'status'):
            cursor.execute("ALTER TABLE attendance ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'Present'")

        if not table_exists(cursor, 'payroll'):
            cursor.execute(
                """
                CREATE TABLE payroll (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL UNIQUE,
                    yearly_salary FLOAT NOT NULL DEFAULT 0.0,
                    daily_salary FLOAT NOT NULL DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(employee_id) REFERENCES user(id)
                )
                """
            )

        if not table_exists(cursor, 'salary_deductions'):
            cursor.execute(
                """
                CREATE TABLE salary_deductions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    amount FLOAT NOT NULL DEFAULT 0.0,
                    status VARCHAR(20) NOT NULL DEFAULT 'DEDUCTED',
                    reason VARCHAR(100) NOT NULL DEFAULT 'absent',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(employee_id) REFERENCES user(id)
                )
                """
            )

        if not table_exists(cursor, 'incentives'):
            cursor.execute(
                """
                CREATE TABLE incentives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    amount FLOAT NOT NULL DEFAULT 0.0,
                    reason VARCHAR(255),
                    month VARCHAR(7) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(employee_id) REFERENCES user(id)
                )
                """
            )

        if not table_exists(cursor, 'leave_requests'):
            cursor.execute(
                """
                CREATE TABLE leave_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    leave_date DATE NOT NULL,
                    subject VARCHAR(200) NOT NULL,
                    message TEXT NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(employee_id) REFERENCES user(id)
                )
                """
            )

        conn.commit()
        print('✓ Payroll migration completed successfully')
    finally:
        conn.close()


if __name__ == '__main__':
    run()
