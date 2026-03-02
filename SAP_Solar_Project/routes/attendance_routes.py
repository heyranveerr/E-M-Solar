from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.attendance import Attendance
from datetime import datetime, date, timedelta

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance')
@login_required
def attendance():
    is_admin = current_user.username == 'admin'
    
    if is_admin:
        return redirect(url_for('attendance.attendance_admin'))
    else:
        # Employee view - show their own attendance
        today = date.today()
        today_attendance = Attendance.query.filter(
            (Attendance.employee_id == current_user.id) & 
            (Attendance.date == today)
        ).first()
        
        # Get recent attendance records (last 30 days)
        thirty_days_ago = today - timedelta(days=30)
        recent_attendance = Attendance.query.filter(
            (Attendance.employee_id == current_user.id) &
            (Attendance.date >= thirty_days_ago)
        ).order_by(Attendance.date.desc()).all()
        
        return render_template('attendance.html', 
                             today_attendance=today_attendance,
                             recent_attendance=recent_attendance,
                             today=today)

@attendance_bp.route('/attendance/admin')
@login_required
def attendance_admin():
    is_admin = current_user.username == 'admin'
    if not is_admin:
        flash('You do not have permission to access this page')
        return redirect(url_for('attendance.attendance'))
    
    # Get filter parameters
    filter_date = request.args.get('filter_date')
    filter_employee = request.args.get('filter_employee')
    
    # Base query
    query = Attendance.query
    
    # Apply filters
    if filter_date:
        try:
            filter_date_obj = datetime.strptime(filter_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.date == filter_date_obj)
        except ValueError:
            pass
    
    if filter_employee:
        query = query.filter(Attendance.employee_id == filter_employee)
    
    # Get all attendance records
    attendance_records = query.order_by(Attendance.date.desc(), Attendance.check_in.desc()).all()
    
    # Get all employees for filter dropdown
    from models.user import User
    employees = User.query.filter(User.username != 'admin').all()
    
    # Calculate summary statistics
    total_records = len(attendance_records)
    employees_present_today = 0
    employees_absent_today = 0
    
    if not filter_date:
        today = date.today()
        today_attendance = Attendance.query.filter(Attendance.date == today).all()
        employees_present_today = len(set([att.employee_id for att in today_attendance]))
        employees_absent_today = len(employees) - employees_present_today
    
    return render_template('attendance_admin.html',
                         attendance_records=attendance_records,
                         employees=employees,
                         filter_date=filter_date,
                         filter_employee=filter_employee,
                         total_records=total_records,
                         employees_present_today=employees_present_today,
                         employees_absent_today=employees_absent_today)

@attendance_bp.route('/attendance/check-in', methods=['POST'])
@login_required
def check_in():
    """Employee check-in endpoint"""
    try:
        today = date.today()
        
        # Check if already checked in today
        existing_attendance = Attendance.query.filter(
            (Attendance.employee_id == current_user.id) &
            (Attendance.date == today)
        ).first()
        
        if existing_attendance:
            return jsonify({
                'success': False,
                'message': 'You have already checked in today at ' + 
                          existing_attendance.check_in.strftime('%I:%M:%S %p')
            })
        
        # Create new attendance record
        attendance = Attendance(
            employee_id=current_user.id,
            date=today,
            check_in=datetime.now()
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Check-in successful',
            'check_in_time': attendance.check_in.strftime('%I:%M:%S %p')
        })
    except Exception as e:
        print(f"Error during check-in: {e}")
        return jsonify({'success': False, 'message': str(e)})

@attendance_bp.route('/attendance/check-out', methods=['POST'])
@login_required
def check_out():
    """Employee check-out endpoint"""
    try:
        today = date.today()
        
        # Find today's attendance record
        attendance = Attendance.query.filter(
            (Attendance.employee_id == current_user.id) &
            (Attendance.date == today)
        ).first()
        
        if not attendance:
            return jsonify({
                'success': False,
                'message': 'No check-in record found. Please check in first.'
            })
        
        if attendance.check_out:
            return jsonify({
                'success': False,
                'message': 'You have already checked out at ' + 
                          attendance.check_out.strftime('%I:%M:%S %p')
            })
        
        # Set check-out time and calculate total hours
        attendance.check_out = datetime.now()
        attendance.calculate_total_hours()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Check-out successful',
            'check_out_time': attendance.check_out.strftime('%I:%M:%S %p'),
            'total_hours': round(attendance.total_hours, 2)
        })
    except Exception as e:
        print(f"Error during check-out: {e}")
        return jsonify({'success': False, 'message': str(e)})
