from extensions import db
from datetime import datetime

class CRMReminder(db.Model):
    __tablename__ = 'crm_reminder'
    
    id = db.Column(db.Integer, primary_key=True)
    crm_id = db.Column(db.Integer, db.ForeignKey('crm.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    reminder_datetime = db.Column(db.DateTime, nullable=False)
    reminder_text = db.Column(db.Text, nullable=False)
    is_dismissed = db.Column(db.Boolean, default=False)
    is_seen = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    crm = db.relationship('CRM', back_populates='reminders')
    user = db.relationship('User', backref='reminders')
    
    def __repr__(self):
        return f'<CRMReminder {self.id}: CRM {self.crm_id} for User {self.user_id}>'
