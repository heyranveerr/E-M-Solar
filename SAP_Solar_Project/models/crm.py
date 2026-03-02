from extensions import db
from datetime import datetime

class CRM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ivrs_number = db.Column('ivrm_number', db.String(100), nullable=True)
    calling_by = db.Column(db.String(100), nullable=True)
    employee_name = db.Column(db.String(100), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    pincode = db.Column(db.String(20), nullable=True)
    mobile_number = db.Column(db.String(20), nullable=True)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(50), nullable=False, default='Pending')
    
    # Existing connection details
    connection_category = db.Column(db.String(100), nullable=True)
    arrears = db.Column(db.String(100), nullable=True)
    connection_phase = db.Column(db.String(50), nullable=True)
    connected_load = db.Column(db.String(100), nullable=True)
    connected_load_unit = db.Column(db.String(50), nullable=True)
    
    # Meter Details
    meter_identifier = db.Column(db.String(100), nullable=True)
    meter_make = db.Column(db.String(100), nullable=True)
    meter_type = db.Column(db.String(100), nullable=True)
    meter_capacity = db.Column(db.String(100), nullable=True)
    
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
