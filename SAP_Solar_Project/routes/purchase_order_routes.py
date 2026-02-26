from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models.purchase_order import PurchaseOrder, PurchaseOrderItem
from extensions import db
from datetime import datetime

purchase_order_bp = Blueprint('purchase_order_bp', __name__)

@purchase_order_bp.route('/purchase_orders', methods=['GET'])
def get_purchase_orders():
    purchase_orders = PurchaseOrder.query.all()
    return render_template('purchase_orders.html', purchase_orders=purchase_orders)

@purchase_order_bp.route('/purchase_orders/new', methods=['GET'])
def create_purchase_order_form():
    return render_template('purchase_order_form.html', po=None)

@purchase_order_bp.route('/purchase_orders', methods=['POST'])
def create_purchase_order():
    po_date_str = request.form['po_date']
    po_date = datetime.strptime(po_date_str, '%Y-%m-%d').date() if po_date_str else None
    
    new_po = PurchaseOrder(
        po_number=request.form['po_number'],
        po_date=po_date,
        vendor_name=request.form['vendor_name'],
        vendor_code=request.form['vendor_code'],
        shipped_to_name=request.form['shipped_to_name'],
        shipped_to_address=request.form['shipped_to_address'],
        bill_to_name=request.form['bill_to_name'],
        bill_to_address=request.form['bill_to_address'],
        total_tax_amount=float(request.form.get('total_tax_amount', 0)),
        grand_total=float(request.form['grand_total']),
        iec_code_no=request.form.get('iec_code_no'),
        contact_person=request.form.get('contact_person'),
        contact_email_id=request.form.get('contact_email_id'),
        payment_terms=request.form.get('payment_terms'),
        inco_terms=request.form.get('inco_terms'),
        header_text=request.form.get('header_text')
    )
    db.session.add(new_po)
    db.session.commit()
    return redirect(url_for('purchase_order_bp.get_purchase_orders'))

@purchase_order_bp.route('/purchase_orders/<int:id>', methods=['GET'])
def get_purchase_order(id):
    po = PurchaseOrder.query.get_or_404(id)
    return render_template('purchase_order_detail.html', po=po)

@purchase_order_bp.route('/purchase_orders/<int:id>/edit', methods=['GET'])
def edit_purchase_order_form(id):
    po = PurchaseOrder.query.get_or_404(id)
    return render_template('purchase_order_form.html', po=po)

@purchase_order_bp.route('/purchase_orders/<int:id>/edit', methods=['POST'])
def update_purchase_order(id):
    po = PurchaseOrder.query.get_or_404(id)
    po.po_number = request.form['po_number']
    po_date_str = request.form['po_date']
    po.po_date = datetime.strptime(po_date_str, '%Y-%m-%d').date() if po_date_str else None
    po.vendor_name = request.form['vendor_name']
    po.vendor_code = request.form['vendor_code']
    po.shipped_to_name = request.form['shipped_to_name']
    po.shipped_to_address = request.form['shipped_to_address']
    po.bill_to_name = request.form['bill_to_name']
    po.bill_to_address = request.form['bill_to_address']
    po.total_tax_amount = float(request.form.get('total_tax_amount', 0))
    po.grand_total = float(request.form['grand_total'])
    po.iec_code_no = request.form.get('iec_code_no')
    po.contact_person = request.form.get('contact_person')
    po.contact_email_id = request.form.get('contact_email_id')
    po.payment_terms = request.form.get('payment_terms')
    po.inco_terms = request.form.get('inco_terms')
    po.header_text = request.form.get('header_text')
    db.session.commit()
    return redirect(url_for('purchase_order_bp.get_purchase_order', id=po.id))

@purchase_order_bp.route('/purchase_orders/<int:id>/delete', methods=['POST'])
def delete_purchase_order(id):
    po = PurchaseOrder.query.get_or_404(id)
    db.session.delete(po)
    db.session.commit()
    return redirect(url_for('purchase_order_bp.get_purchase_orders'))

@purchase_order_bp.route('/purchase_orders/<int:id>/add_item', methods=['GET', 'POST'])
def add_purchase_order_item(id):
    po = PurchaseOrder.query.get_or_404(id)
    if request.method == 'POST':
        try:
            new_item = PurchaseOrderItem(
                po_id=po.id,
                material_code=request.form.get('material_code', ''),
                description=request.form['description'],
                hsn_sac=request.form.get('hsn_sac', ''),
                unit=request.form['unit'],
                quantity=float(request.form['quantity']),
                rate=float(request.form['rate']),
                discount=float(request.form.get('discount', 0)),
                taxable_value=float(request.form['taxable_value']),
                igst_rate=float(request.form.get('igst_rate', 0)),
                igst_amount=float(request.form.get('igst_amount', 0)),
                sub_total=float(request.form['sub_total'])
            )
            db.session.add(new_item)
            db.session.commit()
            return redirect(url_for('purchase_order_bp.get_purchase_order', id=po.id))
        except Exception as e:
            db.session.rollback()
            return render_template('purchase_order_item_form.html', po=po, error=str(e))
    return render_template('purchase_order_item_form.html', po=po)

@purchase_order_bp.route('/purchase_order_items/<int:id>', methods=['GET'])
def get_purchase_order_item(id):
    item = PurchaseOrderItem.query.get_or_404(id)
    return render_template('purchase_order_item_detail.html', item=item)