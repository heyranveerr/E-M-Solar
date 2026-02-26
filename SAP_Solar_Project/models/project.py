from extensions import db
from sqlalchemy.orm import relationship

class SolarProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    capacity_mw = db.Column(db.String(50))  # Changed to String to accommodate AC/DC format
    budget = db.Column(db.Float)
    status = db.Column(db.String(50))
    # Fields for PDF linking (now to be used for summary data)
    boq_pdf_path = db.Column(db.String(255)) # This field name is misleading now, but keeping for continuity for now
    bbu_pdf_path = db.Column(db.String(255)) # This field name is misleading now, but keeping for continuity for now
    # New fields for BBU finance summary
    finance_supply_price = db.Column(db.Float)
    finance_service_price = db.Column(db.Float)
    finance_total_price = db.Column(db.Float)
    
    purchase_orders = relationship("PurchaseOrder", back_populates="project")
    finance_transactions = relationship("FinanceTransaction", back_populates="project")
    materials = relationship("Material", back_populates="project")
    bbu_supply_items = relationship("BBUSupplyItem", back_populates="project")
    bbu_service_items = relationship("BBUServiceItem", back_populates="project")
