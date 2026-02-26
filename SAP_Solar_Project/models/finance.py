from extensions import db
from sqlalchemy.orm import relationship

class FinanceTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('solar_project.id'))
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'))
    transaction_type = db.Column(db.String(50))
    amount = db.Column(db.Float)
    date = db.Column(db.Date)
    description = db.Column(db.String(200))

    project = relationship("SolarProject", back_populates="finance_transactions")
