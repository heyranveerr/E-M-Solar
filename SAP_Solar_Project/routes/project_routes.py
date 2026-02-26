from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models.project import SolarProject
from models.material import Material
from models.bbu_item import BBUSupplyItem, BBUServiceItem
from extensions import db
import pandas as pd
import os

project_bp = Blueprint('project_bp', __name__)

UPLOAD_FOLDER = 'SAP_Solar_Project/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@project_bp.route('/projects', methods=['GET'])
def get_projects():
    projects = SolarProject.query.all()
    print("Projects queried:", projects)
    return render_template('projects.html', projects=projects)

@project_bp.route('/projects/new', methods=['GET'])
def add_project_form():
    return render_template('project_form.html', project=None)

@project_bp.route('/projects', methods=['POST'])
def create_project():
    print("Form data:", request.form)
    # Helper function to parse float with optional commas
    def parse_float_with_commas(value):
        if value:
            return float(value.replace(',', ''))
        return None

    try:
        capacity_mw_str = request.form.get('capacity_mw')
        budget_str = request.form.get('budget')
        new_project = SolarProject(
            name=request.form.get('name'),
            capacity_mw= (capacity_mw_str) if capacity_mw_str and capacity_mw_str.strip() else None,
            budget=float(budget_str) if budget_str and budget_str.strip() else None,
            status=request.form.get('status'),
            finance_supply_price=parse_float_with_commas(request.form.get('finance_supply_price')),
            finance_service_price=parse_float_with_commas(request.form.get('finance_service_price')),
            finance_total_price=parse_float_with_commas(request.form.get('finance_total_price'))
        )
        print("Creating project:", new_project.name)
        db.session.add(new_project)
        db.session.commit()
        db.session.close()
        print("Project committed")
        return redirect(url_for('project_bp.get_projects'))
    except Exception as e:
        print("Exception in create_project:", e)
        db.session.rollback()
        return render_template('project_form.html', error=str(e), project=None)

@project_bp.route('/projects/<int:id>', methods=['GET'])
def get_project(id):
    project = SolarProject.query.get_or_404(id)
    return render_template('project_detail.html', project=project, materials=project.materials, 
                           finance_transactions=project.finance_transactions,
                           bbu_supply_items=project.bbu_supply_items,
                           bbu_service_items=project.bbu_service_items)

@project_bp.route('/projects/<int:id>/edit', methods=['GET'])
def edit_project_form(id):
    project = SolarProject.query.get_or_404(id)
    return render_template('project_form.html', project=project)

@project_bp.route('/projects/<int:id>/edit', methods=['POST'])
def update_project(id):
    # Helper function to parse float with optional commas
    def parse_float_with_commas(value):
        if value:
            return float(value.replace(',', ''))
        return None

    project = SolarProject.query.get_or_404(id)
    project.name = request.form['name']
    project.capacity_mw = (request.form['capacity_mw']) if request.form.get('capacity_mw') else None
    project.budget = float(request.form['budget']) if request.form.get('budget') else None
    project.status = request.form['status']
    project.finance_supply_price = parse_float_with_commas(request.form.get('finance_supply_price'))
    project.finance_service_price = parse_float_with_commas(request.form.get('finance_service_price'))
    project.finance_total_price = parse_float_with_commas(request.form.get('finance_total_price'))
    db.session.commit()
    return redirect(url_for('project_bp.get_project', id=project.id))

@project_bp.route('/projects/<int:id>/delete', methods=['POST'])
def delete_project(id):
    project = SolarProject.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('project_bp.get_projects'))

@project_bp.route('/projects/<int:id>/import_materials', methods=['GET', 'POST'])
def import_materials(id):
    # Helper function to parse float with optional commas and spaces
    def parse_float_with_commas(value):
        if value and isinstance(value, str):
            return float(value.replace(',', '').strip())
        return None

    project = SolarProject.query.get_or_404(id)
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('material_import_form.html', project=project, error="No file part")
        
        file = request.files['file']
        if file.filename == '':
            return render_template('material_import_form.html', project=project, error="No selected file")
        
        if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.csv')):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            try:
                if file.filename.endswith('.xlsx'):
                    df = pd.read_excel(filepath, header=6) # header=6 for 0-based index 7
                else: # .csv
                    df = pd.read_csv(filepath, header=6) # Assuming similar structure for CSV

                # Filter out rows with empty "Item Description" or non-numeric S.No.
                df = df[df['Item Description'].notna() & df['S.No.'].notna()]

                for index, row in df.iterrows():
                    # Skip rows where Item Description is not a material item (e.g., section headers)
                    if not str(row.get('Item Description')).strip() or str(row.get('Item Description')).strip().lower() in ['pv section', ' structures, walkway railing & life line ', 'dc side - cables & accessories', 'ac side - cables & accessories ', 'earthing- cables lugs - lumpsum items', 'miscellaneous', 'earthing & lightning protection', 'module cleaning system', 'i&c']:
                        continue
                    material = Material(
                        project_id=project.id,
                        name=str(row['Item Description']).strip(),
                        specification=str(row['SPECIFICATION']).strip() if pd.notna(row.get('SPECIFICATION')) else None,
                        qty_process_p=str(row['Qty']).strip() if pd.notna(row.get('Qty')) else None,
                        qty_fmg1=str(row['Qty.1']).strip() if pd.notna(row.get('Qty.1')) else None,
                        qty_storage=str(row['Qty.2']).strip() if pd.notna(row.get('Qty.2')) else None,
                        total_qty=str(row['Total ']).strip() if pd.notna(row.get('Total ')) else None,
                        uom=str(row['UOM']).strip() if pd.notna(row.get('UOM')) else None,
                        make=str(row['MAKE']).strip() if pd.notna(row.get('MAKE')) else None,
                        supply=str(row[' Supply ']).strip() if pd.notna(row.get(' Supply ')) else None,
                        service=str(row[' Service ']).strip() if pd.notna(row.get(' Service ')) else None,
                        rate=str(row['Rate ']).strip() if pd.notna(row.get('Rate ')) else None,
                        amount=str(row['Amount ']).strip() if pd.notna(row.get('Amount ')) else None
                    )
                    db.session.add(material)
                db.session.commit()
                flash('Materials imported successfully!')
                return redirect(url_for('project_bp.get_project', id=project.id))

            except Exception as e:
                db.session.rollback()
                return render_template('material_import_form.html', project=project, error=f"Error importing materials: {e}")
            finally:
                os.remove(filepath)
        else:
            return render_template('material_import_form.html', project=project, error="Invalid file type. Please upload an Excel (.xlsx) or CSV (.csv) file.")
    
    return render_template('material_import_form.html', project=project)

@project_bp.route('/projects/<int:id>/import_bbu_supply', methods=['GET', 'POST'])
def import_bbu_supply(id):
    # Helper function to parse percentage values like '18%' to float 18.0
    def parse_percentage(value):
        if value and isinstance(value, str):
            return float(value.replace('%', '').strip())
        return float(value) if value else None

    project = SolarProject.query.get_or_404(id)
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('bbu_supply_import_form.html', project=project, error="No file part")
        
        file = request.files['file']
        if file.filename == '':
            return render_template('bbu_supply_import_form.html', project=project, error="No selected file")
        
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            try:
                df = pd.read_csv(filepath)
                
                for index, row in df.iterrows():
                    item = BBUSupplyItem(
                        project_id=project.id,
                        sl_no=row['Sl No.'],
                        item_description=row['Item Description'],
                        qty=float(row['Qty']),
                        uom=row['UOM'],
                        price=float(row['Price']),
                        taxable_value=float(row['Taxable Value']),
                        gst_rate=parse_percentage(row['GST Rate']),
                        gst_amount=float(row['GST Amount']),
                        total_amount=float(row['Total Amount'])
                    )
                    db.session.add(item)
                db.session.commit()
                flash('BBU Supply Items imported successfully!')
                return redirect(url_for('project_bp.get_project', id=project.id))

            except Exception as e:
                db.session.rollback()
                return render_template('bbu_supply_import_form.html', project=project, error=f"Error importing BBU Supply items: {e}")
            finally:
                os.remove(filepath)
        else:
            return render_template('bbu_supply_import_form.html', project=project, error="Invalid file type. Please upload a CSV (.csv) file.")
    
    return render_template('bbu_supply_import_form.html', project=project)

@project_bp.route('/projects/<int:id>/import_bbu_service', methods=['GET', 'POST'])
def import_bbu_service(id):
    # Helper function to parse percentage values like '18%' to float 18.0
    def parse_percentage(value):
        if value and isinstance(value, str):
            return float(value.replace('%', '').strip())
        return float(value) if value else None

    project = SolarProject.query.get_or_404(id)
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('bbu_service_import_form.html', project=project, error="No file part")
        
        file = request.files['file']
        if file.filename == '':
            return render_template('bbu_service_import_form.html', project=project, error="No selected file")
        
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            try:
                df = pd.read_csv(filepath)
                
                for index, row in df.iterrows():
                    item = BBUServiceItem(
                        project_id=project.id,
                        sl_no=row['Sl No.'],
                        item_description=row['Item Description'],
                        qty=float(row['Qty']),
                        uom=row['UOM'],
                        price=float(row['Price']),
                        taxable_value=float(row['Taxable Value']),
                        gst_rate=parse_percentage(row['GST Rate']),
                        gst_amount=float(row['GST Amount']),
                        total_amount=float(row['Total Amount'])
                    )
                    db.session.add(item)
                db.session.commit()
                flash('BBU Service Items imported successfully!')
                return redirect(url_for('project_bp.get_project', id=project.id))

            except Exception as e:
                db.session.rollback()
                return render_template('bbu_service_import_form.html', project=project, error=f"Error importing BBU Service items: {e}")
            finally:
                os.remove(filepath)
        else:
            return render_template('bbu_service_import_form.html', project=project, error="Invalid file type. Please upload a CSV (.csv) file.")
    
    return render_template('bbu_service_import_form.html', project=project)
