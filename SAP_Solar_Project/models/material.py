from extensions import db
from sqlalchemy.orm import relationship

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('solar_project.id'))
    name = db.Column(db.String(256))
    specification = db.Column(db.String(256))
    qty_process_p = db.Column(db.String(50))
    qty_fmg1 = db.Column(db.String(50))
    qty_storage = db.Column(db.String(50))
    total_qty = db.Column(db.String(100))
    uom = db.Column(db.String(50))
    make = db.Column(db.String(100))
    supply = db.Column(db.String(100))
    service = db.Column(db.String(100))
    rate = db.Column(db.String(50))
    amount = db.Column(db.String(50))

    project = relationship("SolarProject", back_populates="materials")
