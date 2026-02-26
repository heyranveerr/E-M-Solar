from extensions import db
from datetime import datetime

class CRM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(50), nullable=False, default='Pending')
    ivrm_number = db.Column(db.String(100), nullable=True)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    accepted_at = db.Column(db.DateTime, nullable=True)
    is_closed = db.Column(db.Boolean, default=False)
    closed_at = db.Column(db.DateTime, nullable=True)
    is_non_responding = db.Column(db.Boolean, default=False)
    marked_non_responding_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to remarks
    remarks = db.relationship('CRMRemark', back_populates='crm', cascade="all, delete-orphan", lazy=True)
    reminders = db.relationship('CRMReminder', back_populates='crm', cascade="all, delete-orphan", lazy=True)
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id])

    def __repr__(self):
        return f'<CRM {self.id}: {self.employee_name} - {self.customer_name}>'
