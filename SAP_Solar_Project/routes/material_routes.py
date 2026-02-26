from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from models.material import Material
from extensions import db

material_bp = Blueprint('material_bp', __name__)

@material_bp.route('/materials', methods=['GET'])
def get_materials():
    materials = Material.query.all()
    return render_template('materials.html', materials=materials)

@material_bp.route('/materials/new', methods=['GET'])
def add_material_form():
    project_id = request.args.get('project_id')
    return render_template('material_form.html', project_id=project_id)

@material_bp.route('/materials', methods=['POST'])
def create_material():
    project_id = request.form.get('project_id')
    new_material = Material(
        project_id=project_id if project_id else None,
        name=request.form['name'],
        specification=request.form['specification'],
        qty_process_p=request.form.get('qty_process_p'),
        qty_fmg1=request.form.get('qty_fmg1'),
        qty_storage=request.form.get('qty_storage'),
        total_qty=request.form.get('total_qty'),
        uom=request.form['uom'],
        make=request.form['make'],
        supply=request.form.get('supply'),
        service=request.form.get('service'),
        rate=request.form.get('rate'),
        amount=request.form.get('amount')
    )
    db.session.add(new_material)
    db.session.commit()
    if project_id:
        return redirect(url_for('project_bp.get_project', id=project_id))
    return redirect(url_for('material_bp.get_materials'))

@material_bp.route('/materials/<int:id>', methods=['GET'])
def get_material(id):
    material = Material.query.get_or_404(id)
    return render_template('material_detail.html', material=material)

@material_bp.route('/materials/<int:id>/edit', methods=['GET'])
def edit_material_form(id):
    material = Material.query.get_or_404(id)
    return render_template('material_form.html', material=material, project_id=material.project_id)

@material_bp.route('/materials/<int:id>/edit', methods=['POST'])
def update_material(id):
    material = Material.query.get_or_404(id)
    material.name = request.form['name']
    material.specification = request.form['specification']
    material.qty_process_p = request.form.get('qty_process_p')
    material.qty_fmg1 = request.form.get('qty_fmg1')
    material.qty_storage = request.form.get('qty_storage')
    material.total_qty = request.form.get('total_qty')
    material.uom = request.form['uom']
    material.make = request.form['make']
    material.supply = request.form.get('supply')
    material.service = request.form.get('service')
    material.rate = request.form.get('rate')
    material.amount = request.form.get('amount')
    db.session.commit()
    if material.project_id:
        return redirect(url_for('project_bp.get_project', id=material.project_id))
    return redirect(url_for('material_bp.get_material', id=material.id))

@material_bp.route('/materials/<int:id>/delete', methods=['POST'])
def delete_material(id):
    material = Material.query.get_or_404(id)
    project_id = material.project_id
    db.session.delete(material)
    db.session.commit()
    if project_id:
        return redirect(url_for('project_bp.get_project', id=project_id))
    return redirect(url_for('material_bp.get_materials'))
