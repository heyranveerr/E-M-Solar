from extensions import db
from sqlalchemy.orm import relationship

class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('solar_project.id'))
    po_number = db.Column(db.String(50))
    po_date = db.Column(db.Date)
    vendor_name = db.Column(db.String(100))
    vendor_code = db.Column(db.String(50))
    shipped_to_name = db.Column(db.String(100))
    shipped_to_address = db.Column(db.String(200))
    bill_to_name = db.Column(db.String(100))
    bill_to_address = db.Column(db.String(200))
    total_tax_amount = db.Column(db.Float)
    grand_total = db.Column(db.Float)
    iec_code_no = db.Column(db.String(50))
    contact_person = db.Column(db.String(100))
    contact_email_id = db.Column(db.String(100))
    payment_terms = db.Column(db.String(200))
    inco_terms = db.Column(db.String(200))
    header_text = db.Column(db.String(500))

    project = relationship("SolarProject", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order")

class PurchaseOrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'))
    material_code = db.Column(db.String(50))
    description = db.Column(db.String(256))
    hsn_sac = db.Column(db.String(50))
    unit = db.Column(db.String(50))
    quantity = db.Column(db.Float)
    rate = db.Column(db.Float)
    discount = db.Column(db.Float)
    taxable_value = db.Column(db.Float)
    igst_rate = db.Column(db.Float)
    igst_amount = db.Column(db.Float)
    sub_total = db.Column(db.Float)

    purchase_order = relationship("PurchaseOrder", back_populates="items")
