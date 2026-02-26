from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    # Add status column to crm table
    db.session.execute(text('ALTER TABLE crm ADD COLUMN status VARCHAR(50) DEFAULT "Pending"'))
    db.session.commit()
    print('Status column added to crm table')

