from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from models.finance import FinanceTransaction
from extensions import db
from datetime import datetime

finance_bp = Blueprint('finance_bp', __name__)

@finance_bp.route('/finance', methods=['GET'])
def get_transactions():
    transactions = FinanceTransaction.query.all()
    return render_template('finance.html', transactions=transactions)

@finance_bp.route('/finance/new', methods=['GET'])
def add_transaction_form():
    project_id = request.args.get('project_id')
    return render_template('finance_form.html', project_id=project_id, transaction=None)

@finance_bp.route('/finance', methods=['POST'])
def create_transaction():
    project_id = request.form.get('project_id')
    new_transaction = FinanceTransaction(
        project_id=project_id if project_id else None,
        # material_id=request.form['material_id'], # Assuming material_id will be handled in a more complex form or selected
        transaction_type=request.form['transaction_type'],
        amount=float(request.form['amount']) if request.form.get('amount') else None,
        date=datetime.strptime(request.form['date'], '%Y-%m-%d').date() if request.form.get('date') else None,
        description=request.form['description']
    )
    db.session.add(new_transaction)
    db.session.commit()
    if project_id:
        return redirect(url_for('project_bp.get_project', id=project_id))
    return redirect(url_for('finance_bp.get_transactions'))

@finance_bp.route('/finance/<int:id>', methods=['GET'])
def get_transaction(id):
    transaction = FinanceTransaction.query.get_or_404(id)
    return render_template('finance_detail.html', transaction=transaction)

@finance_bp.route('/finance/<int:id>/edit', methods=['GET'])
def edit_transaction_form(id):
    transaction = FinanceTransaction.query.get_or_404(id)
    return render_template('finance_form.html', transaction=transaction, project_id=transaction.project_id)

@finance_bp.route('/finance/<int:id>/edit', methods=['POST'])
def update_transaction(id):
    transaction = FinanceTransaction.query.get_or_404(id)
    # project_id = request.form.get('project_id') # project_id should not change on edit of transaction
    transaction.transaction_type = request.form['transaction_type']
    transaction.amount = float(request.form['amount']) if request.form.get('amount') else None
    transaction.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date() if request.form.get('date') else None
    transaction.description = request.form['description']
    db.session.commit()
    if transaction.project_id:
        return redirect(url_for('project_bp.get_project', id=transaction.project_id))
    return redirect(url_for('finance_bp.get_transaction', id=transaction.id))

@finance_bp.route('/finance/<int:id>/delete', methods=['POST'])
def delete_transaction(id):
    transaction = FinanceTransaction.query.get_or_404(id)
    project_id = transaction.project_id
    db.session.delete(transaction)
    db.session.commit()
    if project_id:
        return redirect(url_for('project_bp.get_project', id=project_id))
    return redirect(url_for('finance_bp.get_transactions'))
