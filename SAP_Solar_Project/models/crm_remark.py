from extensions import db
from datetime import datetime

class CRMRemark(db.Model):
    __tablename__ = 'crm_remark'
    
    id = db.Column(db.Integer, primary_key=True)
    crm_id = db.Column(db.Integer, db.ForeignKey('crm.id', ondelete='CASCADE'), nullable=False)
    remark = db.Column(db.Text, nullable=False)
    remark_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=True)
    
    # Relationship to CRM
    crm = db.relationship('CRM', back_populates='remarks')
    
    def __repr__(self):
        return f'<CRMRemark {self.id}: CRM {self.crm_id}>'
