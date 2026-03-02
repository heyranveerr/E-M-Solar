from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.crm import CRM
from models.crm_remark import CRMRemark
from models.crm_reminder import CRMReminder
from datetime import datetime, timedelta

crm_bp = Blueprint('crm', __name__)

@crm_bp.route('/crm')
@login_required
def crm():
    is_admin = current_user.username == 'admin'
    
    # Get filter parameters
    ivrs_filter = request.args.get('ivrs_filter', '').strip()
    employee_filter = request.args.get('employee_filter', '').strip()
    customer_filter = request.args.get('customer_filter', '').strip()
    date_order = request.args.get('date_order', 'desc')
    
    # Base query
    if is_admin:
        query = CRM.query.filter(CRM.is_non_responding == False)
    else:
        query = CRM.query.filter(
            (CRM.is_non_responding == False) & 
            ((CRM.is_closed == False) | (CRM.assigned_to_id == current_user.id))
        )
    
    # Apply filters
    if ivrs_filter:
        query = query.filter(CRM.ivrs_number.ilike(f'%{ivrs_filter}%'))
    if employee_filter:
        query = query.filter(CRM.employee_name.ilike(f'%{employee_filter}%'))
    if customer_filter:
        query = query.filter(CRM.customer_name.ilike(f'%{customer_filter}%'))
    
    # Apply sorting
    if date_order == 'asc':
        query = query.order_by(CRM.date.asc())
    else:
        query = query.order_by(CRM.date.desc())
    
    crm_entries = query.all()
    return render_template('crm.html', crm_entries=crm_entries, is_admin=is_admin)

@crm_bp.route('/crm/add', methods=['GET', 'POST'])
@login_required
def add_crm():
    if request.method == 'POST':
        employee_name = request.form.get('employee_name')
        calling_by = request.form.get('calling_by')
        customer_name = request.form.get('customer_name')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        mobile_number = request.form.get('mobile_number')
        date_str = request.form.get('date')
        description = request.form.get('description')
        price_str = request.form.get('price')
        status = request.form.get('status')
        ivrs_number = request.form.get('ivrs_number')
        
        # Existing connection details
        connection_category = request.form.get('connection_category')
        arrears = request.form.get('arrears')
        connection_phase = request.form.get('connection_phase')
        connected_load = request.form.get('connected_load')
        connected_load_unit = request.form.get('connected_load_unit')
        
        # Meter Details
        meter_identifier = request.form.get('meter_identifier')
        meter_make = request.form.get('meter_make')
        meter_type = request.form.get('meter_type')
        meter_capacity = request.form.get('meter_capacity')

        if current_user.username == 'admin' and not employee_name:
            employee_name = current_user.username

        if not all([employee_name, customer_name, date_str, description, status]):
            flash('All required fields must be filled')
            return redirect(url_for('crm.add_crm'))

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format')
            return redirect(url_for('crm.add_crm'))

        try:
            price = float(price_str) if price_str else 0.0
        except ValueError:
            flash('Invalid price format')
            return redirect(url_for('crm.add_crm'))

        new_crm = CRM(
            employee_name=employee_name,
            calling_by=calling_by,
            customer_name=customer_name,
            address=address,
            pincode=pincode,
            mobile_number=mobile_number,
            date=date,
            description=description,
            price=price,
            status=status,
            ivrs_number=ivrs_number,
            connection_category=connection_category,
            arrears=arrears,
            connection_phase=connection_phase,
            connected_load=connected_load,
            connected_load_unit=connected_load_unit,
            meter_identifier=meter_identifier,
            meter_make=meter_make,
            meter_type=meter_type,
            meter_capacity=meter_capacity
        )
        if current_user.username != 'admin':
            new_crm.assigned_to_id = current_user.id
            new_crm.accepted_at = datetime.utcnow()
        db.session.add(new_crm)
        db.session.commit()
        flash('CRM entry added successfully')
        return redirect(url_for('crm.crm'))

    return render_template('crm_form.html')

@crm_bp.route('/crm/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_crm(id):
    crm_entry = CRM.query.get_or_404(id)
    is_admin = current_user.username == 'admin'
    is_assignee = crm_entry.assigned_to_id == current_user.id
    if not is_admin and not is_assignee:
        flash('You are not allowed to edit this CRM entry')
        return redirect(url_for('crm.crm'))
    if crm_entry.is_closed:
        flash('Closed CRM entries cannot be edited')
        return redirect(url_for('crm.crm'))

    if request.method == 'POST':
        employee_name = request.form.get('employee_name')
        calling_by = request.form.get('calling_by')
        customer_name = request.form.get('customer_name')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        mobile_number = request.form.get('mobile_number')
        date_str = request.form.get('date')
        description = request.form.get('description')
        price_str = request.form.get('price')
        status = request.form.get('status')
        ivrs_number = request.form.get('ivrs_number')
        
        # Existing connection details
        connection_category = request.form.get('connection_category')
        arrears = request.form.get('arrears')
        connection_phase = request.form.get('connection_phase')
        connected_load = request.form.get('connected_load')
        connected_load_unit = request.form.get('connected_load_unit')
        
        # Meter Details
        meter_identifier = request.form.get('meter_identifier')
        meter_make = request.form.get('meter_make')
        meter_type = request.form.get('meter_type')
        meter_capacity = request.form.get('meter_capacity')

        if not all([employee_name, customer_name, date_str, description, status]):
            flash('All required fields must be filled')
            return redirect(url_for('crm.edit_crm', id=id))

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format')
            return redirect(url_for('crm.edit_crm', id=id))

        try:
            price = float(price_str) if price_str else 0.0
        except ValueError:
            flash('Invalid price format')
            return redirect(url_for('crm.edit_crm', id=id))

        # Update the existing entry directly
        crm_entry.employee_name = employee_name
        crm_entry.calling_by = calling_by
        crm_entry.customer_name = customer_name
        crm_entry.address = address
        crm_entry.pincode = pincode
        crm_entry.mobile_number = mobile_number
        crm_entry.date = date
        crm_entry.description = description
        crm_entry.price = price
        crm_entry.status = status
        crm_entry.ivrs_number = ivrs_number
        crm_entry.connection_category = connection_category
        crm_entry.arrears = arrears
        crm_entry.connection_phase = connection_phase
        crm_entry.connected_load = connected_load
        crm_entry.connected_load_unit = connected_load_unit
        crm_entry.meter_identifier = meter_identifier
        crm_entry.meter_make = meter_make
        crm_entry.meter_type = meter_type
        crm_entry.meter_capacity = meter_capacity
        crm_entry.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('CRM entry updated successfully')
        return redirect(url_for('crm.crm'))

    return render_template('crm_form.html', crm_entry=crm_entry)

@crm_bp.route('/crm/delete/<int:id>', methods=['POST'])
@login_required
def delete_crm(id):
    if current_user.username != 'admin':
        flash('Only admin can delete CRM entries')
        return redirect(url_for('crm.crm'))
    crm_entry = CRM.query.get_or_404(id)
    db.session.delete(crm_entry)
    db.session.commit()
    flash('CRM entry deleted successfully')
    return redirect(url_for('crm.crm'))

@crm_bp.route('/crm/accept/<int:id>', methods=['POST'])
@login_required
def accept_crm(id):
    if current_user.username == 'admin':
        flash('Admin cannot accept CRM entries')
        return redirect(url_for('crm.crm'))

    crm_entry = CRM.query.get_or_404(id)
    if crm_entry.is_closed:
        flash('Cannot accept a closed CRM entry')
        return redirect(url_for('crm.crm'))
    if crm_entry.assigned_to_id is not None:
        flash('This CRM entry is already accepted')
        return redirect(url_for('crm.crm'))

    crm_entry.assigned_to_id = current_user.id
    crm_entry.accepted_at = datetime.utcnow()
    db.session.commit()
    flash('CRM entry accepted successfully')
    return redirect(url_for('crm.crm'))

@crm_bp.route('/crm/close/<int:id>', methods=['POST'])
@login_required
def close_crm(id):
    crm_entry = CRM.query.get_or_404(id)
    is_admin = current_user.username == 'admin'
    is_assignee = crm_entry.assigned_to_id == current_user.id

    if not (is_admin or is_assignee):
        flash('You are not allowed to close this CRM entry')
        return redirect(url_for('crm.crm'))
    if crm_entry.is_closed:
        flash('CRM entry is already closed')
        return redirect(url_for('crm.crm'))
    if crm_entry.status != 'Completed':
        flash('CRM can only be closed after status is Completed')
        return redirect(url_for('crm.crm'))

    crm_entry.is_closed = True
    crm_entry.closed_at = datetime.utcnow()
    db.session.commit()
    flash('CRM entry closed successfully')
    return redirect(url_for('crm.crm'))

@crm_bp.route('/crm/<int:id>/add_remark', methods=['POST'])
@login_required
def add_remark(id):
    crm_entry = CRM.query.get_or_404(id)
    is_admin = current_user.username == 'admin'
    is_assignee = crm_entry.assigned_to_id == current_user.id
    if not is_admin and not is_assignee:
        flash('You are not allowed to add remarks to this CRM entry')
        return redirect(url_for('crm.crm'))
    remark_text = request.form.get('remark')
    remark_date_str = request.form.get('remark_date')
    
    if not remark_text or not remark_text.strip():
        flash('Remark cannot be empty')
        return redirect(url_for('crm.edit_crm', id=id))
    
    if not remark_date_str:
        flash('Remark date is required')
        return redirect(url_for('crm.edit_crm', id=id))
    
    try:
        remark_date = datetime.strptime(remark_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format')
        return redirect(url_for('crm.edit_crm', id=id))
    
    new_remark = CRMRemark(
        crm_id=id,
        remark=remark_text.strip(),
        remark_date=remark_date,
        created_by=current_user.username if current_user.is_authenticated else 'Unknown'
    )
    db.session.add(new_remark)
    db.session.commit()
    flash('Remark added successfully')
    return redirect(url_for('crm.edit_crm', id=id))

@crm_bp.route('/non_responding_customers')
@login_required
def non_responding_customers():
    is_admin = current_user.username == 'admin'
    
    # Get filter parameters
    ivrs_filter = request.args.get('ivrs_filter', '').strip()
    employee_filter = request.args.get('employee_filter', '').strip()
    customer_filter = request.args.get('customer_filter', '').strip()
    date_order = request.args.get('date_order', 'desc')
    
    # Base query
    if is_admin:
        query = CRM.query.filter(CRM.is_non_responding == True)
    else:
        query = CRM.query.filter(
            (CRM.is_non_responding == True) & 
            ((CRM.is_closed == False) | (CRM.assigned_to_id == current_user.id))
        )
    
    # Apply filters
    if ivrs_filter:
        query = query.filter(CRM.ivrs_number.ilike(f'%{ivrs_filter}%'))
    if employee_filter:
        query = query.filter(CRM.employee_name.ilike(f'%{employee_filter}%'))
    if customer_filter:
        query = query.filter(CRM.customer_name.ilike(f'%{customer_filter}%'))
    
    # Apply sorting
    if date_order == 'asc':
        query = query.order_by(CRM.date.asc())
    else:
        query = query.order_by(CRM.date.desc())
    
    crm_entries = query.all()
    return render_template('non_responding_customers.html', crm_entries=crm_entries, is_admin=is_admin)

@crm_bp.route('/crm/mark_non_responding/<int:id>', methods=['POST'])
@login_required
def mark_non_responding(id):
    crm_entry = CRM.query.get_or_404(id)
    is_admin = current_user.username == 'admin'
    is_assignee = crm_entry.assigned_to_id == current_user.id
    
    if not (is_admin or is_assignee):
        flash('You are not allowed to mark this CRM as non-responding')
        return redirect(url_for('crm.crm'))
    
    if crm_entry.is_closed:
        flash('Cannot mark a closed CRM as non-responding')
        return redirect(url_for('crm.crm'))
    
    crm_entry.is_non_responding = True
    crm_entry.marked_non_responding_at = datetime.utcnow()
    db.session.commit()
    flash('CRM marked as non-responding')
    return redirect(url_for('crm.crm'))

@crm_bp.route('/crm/restore_from_non_responding/<int:id>', methods=['POST'])
@login_required
def restore_from_non_responding(id):
    crm_entry = CRM.query.get_or_404(id)
    is_admin = current_user.username == 'admin'
    is_assignee = crm_entry.assigned_to_id == current_user.id
    
    if not (is_admin or is_assignee):
        flash('You are not allowed to restore this CRM')
        return redirect(url_for('crm.non_responding_customers'))
    
    crm_entry.is_non_responding = False
    crm_entry.marked_non_responding_at = None
    db.session.commit()
    flash('CRM restored to active list')
    return redirect(url_for('crm.non_responding_customers'))

@crm_bp.route('/crm/close_non_responding/<int:id>', methods=['POST'])
@login_required
def close_non_responding(id):
    crm_entry = CRM.query.get_or_404(id)
    is_admin = current_user.username == 'admin'
    is_assignee = crm_entry.assigned_to_id == current_user.id
    
    if not (is_admin or is_assignee):
        flash('You are not allowed to close this CRM')
        return redirect(url_for('crm.non_responding_customers'))
    
    if crm_entry.is_closed:
        flash('CRM is already closed')
        return redirect(url_for('crm.non_responding_customers'))
    
    crm_entry.is_closed = True
    crm_entry.closed_at = datetime.utcnow()
    db.session.commit()
    flash('Non-responding CRM closed successfully')
    return redirect(url_for('crm.non_responding_customers'))

@crm_bp.route('/crm/add_reminder/<int:crm_id>', methods=['POST'])
@login_required
def add_reminder(crm_id):
    crm_entry = CRM.query.get_or_404(crm_id)
    
    reminder_date_str = request.form.get('reminder_date')
    reminder_text = request.form.get('reminder_text', '').strip()
    
    if not reminder_date_str or not reminder_text:
        flash('Please provide both reminder date and text')
        return redirect(url_for('crm.edit_crm', id=crm_id))
    
    try:
        # Parse date and set to start of day
        reminder_date = datetime.strptime(reminder_date_str, '%Y-%m-%d')
    except ValueError:
        flash('Invalid date format')
        return redirect(url_for('crm.edit_crm', id=crm_id))
    
    # Check if date is today or in the future
    today = datetime.now().date()
    if reminder_date.date() < today:
        flash('Reminder date must be today or in the future')
        return redirect(url_for('crm.edit_crm', id=crm_id))
    
    reminder = CRMReminder(
        crm_id=crm_id,
        user_id=current_user.id,
        reminder_datetime=reminder_date,
        reminder_text=reminder_text,
        is_dismissed=False
    )
    
    db.session.add(reminder)
    db.session.commit()
    flash('Reminder set successfully')
    return redirect(url_for('crm.edit_crm', id=crm_id))

@crm_bp.route('/crm/get_pending_reminders')
@login_required
def get_pending_reminders():
    """Get pending reminders for current user matching today's date"""
    try:
        today = datetime.now().date()
        today_start = datetime(today.year, today.month, today.day, 0, 0, 0)
        today_end = datetime(today.year, today.month, today.day, 23, 59, 59)
        
        # Get all reminders for current user for today
        reminders = CRMReminder.query.filter(
            CRMReminder.user_id == current_user.id,
            CRMReminder.reminder_datetime >= today_start,
            CRMReminder.reminder_datetime <= today_end
        ).all()
        
        reminder_list = []
        for r in reminders:
            reminder_list.append({
                'id': r.id,
                'crm_id': r.crm_id,
                'crm_name': r.crm.customer_name if r.crm else 'Deleted CRM',
                'reminder_text': r.reminder_text,
                'reminder_date': r.reminder_datetime.strftime('%Y-%m-%d'),
                'is_seen': r.is_seen
            })
        
        return jsonify({'reminders': reminder_list, 'success': True})
    except Exception as e:
        print(f"Error in get_pending_reminders: {e}")
        return jsonify({'reminders': [], 'success': False, 'error': str(e)})

@crm_bp.route('/crm/get_all_reminders')
@login_required
def get_all_reminders():
    """Get all reminders for current user (for bell icon dropdown)"""
    try:
        # Get all unseen and today's reminders
        today = datetime.now().date()
        today_start = datetime(today.year, today.month, today.day, 0, 0, 0)
        
        reminders = CRMReminder.query.filter(
            CRMReminder.user_id == current_user.id
        ).order_by(CRMReminder.reminder_datetime.desc()).all()
        
        # Separate unseen and seen
        unseen = []
        seen = []
        
        for r in reminders:
            reminder_data = {
                'id': r.id,
                'crm_id': r.crm_id,
                'crm_name': r.crm.customer_name if r.crm else 'Deleted CRM',
                'reminder_text': r.reminder_text,
                'reminder_date': r.reminder_datetime.strftime('%Y-%m-%d'),
                'is_seen': r.is_seen
            }
            
            if r.is_seen:
                seen.append(reminder_data)
            else:
                unseen.append(reminder_data)
        
        unseen_count = len(unseen)
        
        return jsonify({
            'unseen': unseen,
            'seen': seen,
            'unseen_count': unseen_count,
            'success': True
        })
    except Exception as e:
        print(f"Error in get_all_reminders: {e}")
        return jsonify({'unseen': [], 'seen': [], 'unseen_count': 0, 'success': False, 'error': str(e)})

@crm_bp.route('/crm/mark_reminder_seen/<int:reminder_id>', methods=['POST'])
@login_required
def mark_reminder_seen(reminder_id):
    """Mark a reminder as seen"""
    try:
        reminder = CRMReminder.query.get_or_404(reminder_id)
        
        if reminder.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Not authorized'})
        
        reminder.is_seen = True
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error marking reminder as seen: {e}")
        return jsonify({'success': False, 'error': str(e)})

@crm_bp.route('/crm/dismiss_reminder/<int:id>', methods=['POST'])
@login_required
def dismiss_reminder(id):
    """This endpoint is now unused - dismissal is handled client-side"""
    return redirect(url_for('crm.crm'))

@crm_bp.route('/crm/lookup_ivrs/<ivrs_number>', methods=['GET'])
@login_required
def lookup_ivrs(ivrs_number):
    """Look up customer details by IVRS number"""
    try:
        # Find the most recent CRM entry with this IVRS number
        crm_entry = CRM.query.filter(CRM.ivrs_number == ivrs_number).order_by(CRM.created_at.desc()).first()
        
        if crm_entry:
            return jsonify({
                'success': True,
                'calling_by': crm_entry.calling_by if crm_entry.calling_by else '',
                'customer_name': crm_entry.customer_name,
                'mobile_number': crm_entry.mobile_number if crm_entry.mobile_number else '',
                'address': crm_entry.address if crm_entry.address else '',
                'pincode': crm_entry.pincode if crm_entry.pincode else '',
                'connection_category': crm_entry.connection_category if crm_entry.connection_category else '',
                'arrears': crm_entry.arrears if crm_entry.arrears else '',
                'connection_phase': crm_entry.connection_phase if crm_entry.connection_phase else '',
                'connected_load': crm_entry.connected_load if crm_entry.connected_load else '',
                'connected_load_unit': crm_entry.connected_load_unit if crm_entry.connected_load_unit else '',
                'meter_identifier': crm_entry.meter_identifier if crm_entry.meter_identifier else '',
                'meter_make': crm_entry.meter_make if crm_entry.meter_make else '',
                'meter_type': crm_entry.meter_type if crm_entry.meter_type else '',
                'meter_capacity': crm_entry.meter_capacity if crm_entry.meter_capacity else ''
            })
        else:
            return jsonify({'success': False, 'message': 'IVRS number not found'})
    except Exception as e:
        print(f"Error looking up IVRS: {e}")
        return jsonify({'success': False, 'error': str(e)})
