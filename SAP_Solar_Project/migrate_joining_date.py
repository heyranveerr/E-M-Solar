"""Migration: add joining_date column to user table."""
from app import create_app
from extensions import db
import sqlalchemy as sa

app = create_app()
with app.app_context():
    with db.engine.connect() as conn:
        cols = [row[1] for row in conn.execute(sa.text("PRAGMA table_info([user])"))]
        if 'joining_date' not in cols:
            conn.execute(sa.text("ALTER TABLE [user] ADD COLUMN joining_date DATE"))
            conn.commit()
            print("joining_date column added successfully.")
        else:
            print("joining_date column already exists.")
