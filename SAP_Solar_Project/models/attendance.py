from extensions import db
from datetime import datetime, timedelta

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.DateTime, nullable=True)
    check_out = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Present')
    total_hours = db.Column(db.Float, nullable=True, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to user
    employee = db.relationship('User', foreign_keys=[employee_id])

    def __repr__(self):
        return f'<Attendance {self.id}: Employee {self.employee_id} - {self.date}>'

    def calculate_total_hours(self):
        """Calculate total working hours if both check-in and check-out are set"""
        if self.check_in and self.check_out:
            duration = self.check_out - self.check_in
            self.total_hours = duration.total_seconds() / 3600  # Convert to hours
        return self.total_hours
