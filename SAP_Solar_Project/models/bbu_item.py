from extensions import db
from sqlalchemy.orm import relationship

class BBUSupplyItem(db.Model):
    __tablename__ = 'bbu_supply_item'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('solar_project.id'))
    sl_no = db.Column(db.String(50))
    item_description = db.Column(db.String(500))
    qty = db.Column(db.Float)
    uom = db.Column(db.String(50))
    price = db.Column(db.Float)
    taxable_value = db.Column(db.Float)
    gst_rate = db.Column(db.String(50)) # Storing as float (e.g., 18.0 for 18%)
    gst_amount = db.Column(db.Float)
    total_amount = db.Column(db.Float)

    project = relationship("SolarProject", back_populates="bbu_supply_items")


class BBUServiceItem(db.Model):
    __tablename__ = 'bbu_service_item'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('solar_project.id'))
    sl_no = db.Column(db.String(50))
    item_description = db.Column(db.String(500))
    qty = db.Column(db.Float)
    uom = db.Column(db.String(50))
    price = db.Column(db.Float)
    taxable_value = db.Column(db.Float)
    gst_rate = db.Column(db.String) # Storing as float (e.g., 18.0 for 18%)
    gst_amount = db.Column(db.Float)
    total_amount = db.Column(db.Float)

    project = relationship("SolarProject", back_populates="bbu_service_items")
