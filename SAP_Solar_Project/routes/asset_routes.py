from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from models.asset import Asset
from extensions import db
from datetime import datetime

asset_bp = Blueprint('asset_bp', __name__)

@asset_bp.route('/assets', methods=['GET'])
def get_assets():
    assets = Asset.query.all()
    return render_template('assets.html', assets=assets)

@asset_bp.route('/assets/new', methods=['GET'])
def add_asset_form():
    return render_template('asset_form.html')

@asset_bp.route('/assets', methods=['POST'])
def create_asset():
    new_asset = Asset(
        asset_name=request.form['asset_name'],
        last_maintenance=datetime.strptime(request.form['last_maintenance'], '%Y-%m-%d').date() if request.form['last_maintenance'] else None,
        status=request.form['status']
    )
    db.session.add(new_asset)
    db.session.commit()
    return redirect(url_for('asset_bp.get_assets'))

@asset_bp.route('/assets/<int:id>', methods=['GET'])
def get_asset(id):
    asset = Asset.query.get_or_404(id)
    return render_template('asset_detail.html', asset=asset)

@asset_bp.route('/assets/<int:id>/edit', methods=['GET'])
def edit_asset_form(id):
    asset = Asset.query.get_or_404(id)
    return render_template('asset_form.html', asset=asset)

@asset_bp.route('/assets/<int:id>/edit', methods=['POST'])
def update_asset(id):
    asset = Asset.query.get_or_404(id)
    asset.asset_name = request.form['asset_name']
    asset.last_maintenance = datetime.strptime(request.form['last_maintenance'], '%Y-%m-%d').date() if request.form['last_maintenance'] else None
    asset.status = request.form['status']
    db.session.commit()
    return redirect(url_for('asset_bp.get_asset', id=asset.id))

@asset_bp.route('/assets/<int:id>/delete', methods=['POST'])
def delete_asset(id):
    asset = Asset.query.get_or_404(id)
    db.session.delete(asset)
    db.session.commit()
    return redirect(url_for('asset_bp.get_assets'))
