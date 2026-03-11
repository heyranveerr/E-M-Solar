import calendar
from datetime import date, datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models.attendance import Attendance
from models.payroll import Incentive, LeaveRequest, Payroll, SalaryDeduction
from models.user import User

payroll_bp = Blueprint('payroll', __name__)

LATE_CHECKIN_CUTOFF_HOUR = 10
LATE_DEDUCTION_RATIO = 0.5


def is_late_checkin(attendance_row):
    if not attendance_row or not attendance_row.check_in:
        return False
    return (
        attendance_row.check_in.hour > LATE_CHECKIN_CUTOFF_HOUR
        or (attendance_row.check_in.hour == LATE_CHECKIN_CUTOFF_HOUR and attendance_row.check_in.minute > 0)
        or (attendance_row.status and 'Late' in attendance_row.status)
    )


def is_admin_user(user):
    return (getattr(user, 'role', 'employee') == 'admin') or (user.username == 'admin')


def days_in_year(year):
    return 366 if calendar.isleap(year) else 365


def parse_month(month_value):
    if not month_value:
        today = date.today()
        return today.year, today.month, f"{today.year:04d}-{today.month:02d}"

    year_part, month_part = month_value.split('-')
    year = int(year_part)
    month = int(month_part)
    return year, month, f"{year:04d}-{month:02d}"


def month_date_range(year, month):
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def working_days(year, month):
    start_date, end_date = month_date_range(year, month)
    days = []
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:
            days.append(current)
        current = date.fromordinal(current.toordinal() + 1)
    return days


def ensure_absence_deductions(employee_id, year, month):
    # Skip calculations for deleted employees
    emp_check = User.query.get(employee_id)
    if emp_check and emp_check.role == 'deleted':
        return

    payroll = Payroll.query.filter_by(employee_id=employee_id).first()
    if not payroll or payroll.yearly_salary <= 0:
        return

    daily_salary = round(payroll.yearly_salary / days_in_year(year), 2)
    payroll.daily_salary = daily_salary

    start_date, end_date = month_date_range(year, month)
    today = date.today()
    if year == today.year and month == today.month:
        end_date = min(end_date, today)

    # Respect employee joining date — don't count days before they joined
    employee = User.query.get(employee_id)
    if employee and employee.joining_date:
        start_date = max(start_date, employee.joining_date)

    attendance_map = {
        row.date: row
        for row in Attendance.query.filter(
            Attendance.employee_id == employee_id,
            Attendance.date >= start_date,
            Attendance.date <= end_date,
            Attendance.check_in.isnot(None),
        ).all()
    }

    approved_leave_days = set()
    for leave in LeaveRequest.query.filter(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.start_date <= end_date,
        LeaveRequest.end_date >= start_date,
        LeaveRequest.status == 'Approved',
    ).all():
        current = max(leave.start_date, start_date)
        while current <= min(leave.end_date, end_date):
            approved_leave_days.add(current)
            current = date.fromordinal(current.toordinal() + 1)

    existing = {
        row.date: row
        for row in SalaryDeduction.query.filter(
            SalaryDeduction.employee_id == employee_id,
            SalaryDeduction.date >= start_date,
            SalaryDeduction.date <= end_date,
        ).all()
    }

    for day in working_days(year, month):
        if day > end_date:
            continue

        existing_row = existing.get(day)
        attendance_row = attendance_map.get(day)

        if day in approved_leave_days:
            if existing_row and existing_row.status == 'DEDUCTED':
                existing_row.status = 'REINSTATED'
            continue

        if attendance_row:
            if is_late_checkin(attendance_row):
                late_amount = round(daily_salary * LATE_DEDUCTION_RATIO, 2)
                if existing_row is None:
                    db.session.add(
                        SalaryDeduction(
                            employee_id=employee_id,
                            date=day,
                            amount=late_amount,
                            status='DEDUCTED',
                            reason='late_check_in',
                        )
                    )
                elif existing_row.status == 'DEDUCTED':
                    existing_row.amount = late_amount
                    existing_row.reason = 'late_check_in'
            elif existing_row and existing_row.status == 'DEDUCTED':
                existing_row.status = 'REINSTATED'
            continue

        if existing_row is None:
            db.session.add(
                SalaryDeduction(
                    employee_id=employee_id,
                    date=day,
                    amount=daily_salary,
                    status='DEDUCTED',
                    reason='absent',
                )
            )


def monthly_totals(employee_id, year, month):
    ensure_absence_deductions(employee_id, year, month)

    payroll = Payroll.query.filter_by(employee_id=employee_id).first()
    monthly_salary = round((payroll.yearly_salary / 12.0), 2) if payroll else 0.0

    start_date, end_date = month_date_range(year, month)

    # Respect joining date
    employee = User.query.get(employee_id)
    if employee and employee.joining_date:
        start_date = max(start_date, employee.joining_date)

    deductions = db.session.query(db.func.coalesce(db.func.sum(SalaryDeduction.amount), 0.0)).filter(
        SalaryDeduction.employee_id == employee_id,
        SalaryDeduction.date >= start_date,
        SalaryDeduction.date <= end_date,
        SalaryDeduction.status == 'DEDUCTED',
    ).scalar()

    incentives = db.session.query(db.func.coalesce(db.func.sum(Incentive.amount), 0.0)).filter(
        Incentive.employee_id == employee_id,
        Incentive.month == f"{year:04d}-{month:02d}",
    ).scalar()

    final_salary = round(monthly_salary + incentives - deductions, 2)

    db.session.commit()

    return {
        'yearly_salary': round(payroll.yearly_salary, 2) if payroll else 0.0,
        'daily_salary': round(payroll.daily_salary, 2) if payroll else 0.0,
        'monthly_salary': monthly_salary,
        'deductions': round(deductions, 2),
        'incentives': round(incentives, 2),
        'final_salary': final_salary,
    }


def monthly_breakdown(employee_id, year, month):
    start_date, end_date = month_date_range(year, month)

    # Respect joining date
    emp = User.query.get(employee_id)
    if emp and emp.joining_date:
        start_date = max(start_date, emp.joining_date)

    attendance_map = {
        row.date: row
        for row in Attendance.query.filter(
            Attendance.employee_id == employee_id,
            Attendance.date >= start_date,
            Attendance.date <= end_date,
        ).all()
    }

    deduction_map = {
        row.date: row
        for row in SalaryDeduction.query.filter(
            SalaryDeduction.employee_id == employee_id,
            SalaryDeduction.date >= start_date,
            SalaryDeduction.date <= end_date,
        ).all()
    }

    # Build leave_map from date ranges
    leave_map = {}
    for leave_request in LeaveRequest.query.filter(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.start_date <= end_date,
        LeaveRequest.end_date >= start_date,
    ).all():
        # Expand date range into individual days
        current = max(leave_request.start_date, start_date)
        while current <= min(leave_request.end_date, end_date):
            leave_map[current] = leave_request
            current = date.fromordinal(current.toordinal() + 1)

    rows = []
    for day in working_days(year, month):
        if day < start_date:
            continue
        leave_request = leave_map.get(day)
        attendance = attendance_map.get(day)
        deduction = deduction_map.get(day)

        status = 'Absent'
        amount = 0.0

        if leave_request and leave_request.status == 'Approved':
            status = 'Approved Leave'
        elif attendance and attendance.check_in:
            is_late = is_late_checkin(attendance)
            status = 'Late Check-In' if is_late else 'Present'
            if deduction and deduction.status == 'DEDUCTED':
                amount = round(deduction.amount, 2)
        elif deduction and deduction.status == 'REINSTATED':
            status = 'Reinstated'
        elif deduction and deduction.status == 'DEDUCTED':
            status = 'Absent'
            amount = round(deduction.amount, 2)

        rows.append({
            'date': day,
            'status': status,
            'check_in_time': attendance.check_in.strftime('%I:%M:%S %p') if attendance and attendance.check_in else '-',
            'deduction': amount,
            'deduction_id': deduction.id if deduction else None,
            'deduction_status': deduction.status if deduction else None,
        })

    return rows


@payroll_bp.route('/payroll/get_pending_leaves')
@login_required
def get_pending_leaves():
    if not is_admin_user(current_user):
        return jsonify({'leaves': [], 'count': 0})
    pending = LeaveRequest.query.filter_by(status='Pending').order_by(LeaveRequest.start_date.asc()).all()
    leaves = []
    for leave in pending:
        employee = User.query.get(leave.employee_id)
        leaves.append({
            'id': leave.id,
            'employee_name': employee.username if employee else 'Unknown',
            'start_date': leave.start_date.strftime('%Y-%m-%d'),
            'end_date': leave.end_date.strftime('%Y-%m-%d'),
            'subject': leave.subject,
        })
    return jsonify({'leaves': leaves, 'count': len(leaves)})


@payroll_bp.route('/payroll')
@login_required
def payroll_home():
    if is_admin_user(current_user):
        return redirect(url_for('payroll.payroll_admin'))

    month_param = request.args.get('month', '')
    year, month, selected_month = parse_month(month_param)
    totals = monthly_totals(current_user.id, year, month)
    breakdown = monthly_breakdown(current_user.id, year, month)

    leaves = LeaveRequest.query.filter_by(employee_id=current_user.id).order_by(LeaveRequest.start_date.desc()).limit(20).all()

    return render_template(
        'payroll_employee.html',
        selected_month=selected_month,
        totals=totals,
        breakdown=breakdown,
        leave_requests=leaves,
    )


@payroll_bp.route('/payroll/leave/apply', methods=['POST'])
@login_required
def apply_leave():
    if is_admin_user(current_user):
        flash('Admins cannot apply leave from this page.')
        return redirect(url_for('payroll.payroll_admin'))
    if current_user.role == 'deleted':
        flash('Inactive account. Cannot submit leave requests.')
        return redirect(url_for('payroll.payroll_home'))

    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    subject = request.form.get('subject', '').strip()
    message = request.form.get('message', '').strip()

    if not start_date_str or not end_date_str or not subject or not message:
        flash('All leave request fields are required.')
        return redirect(url_for('payroll.payroll_home'))

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    if end_date < start_date:
        flash('End date must be on or after start date.')
        return redirect(url_for('payroll.payroll_home'))

    overlapping = LeaveRequest.query.filter(
        LeaveRequest.employee_id == current_user.id,
        LeaveRequest.status == 'Pending',
        LeaveRequest.start_date <= end_date,
        LeaveRequest.end_date >= start_date,
    ).first()
    if overlapping:
        flash('A pending leave request already exists for this date range.')
        return redirect(url_for('payroll.payroll_home'))

    db.session.add(
        LeaveRequest(
            employee_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            subject=subject,
            message=message,
            status='Pending',
        )
    )
    db.session.commit()

    flash('Leave request submitted.')
    return redirect(url_for('payroll.payroll_home'))


@payroll_bp.route('/payroll/admin')
@login_required
def payroll_admin():
    if not is_admin_user(current_user):
        flash('You do not have permission to access this page.')
        return redirect(url_for('payroll.payroll_home'))

    month_param = request.args.get('month', '')
    year, month, selected_month = parse_month(month_param)
    name_filter = request.args.get('name_filter', '').strip()
    salary_sort = request.args.get('salary_sort', '')

    employees = User.query.filter(User.username != 'admin').order_by(User.username.asc()).all()

    payroll_rows = []
    for employee in employees:
        totals = monthly_totals(employee.id, year, month)
        payroll_rows.append(
            {
                'employee': employee,
                'yearly_salary': totals['yearly_salary'],
                'monthly_salary': totals['monthly_salary'],
                'deductions': totals['deductions'],
                'incentives': totals['incentives'],
                'final_salary': totals['final_salary'],
            }
        )

    if name_filter:
        payroll_rows = [r for r in payroll_rows if name_filter.lower() in r['employee'].username.lower()]

    if salary_sort == 'asc':
        payroll_rows.sort(key=lambda r: r['yearly_salary'])
    elif salary_sort == 'desc':
        payroll_rows.sort(key=lambda r: r['yearly_salary'], reverse=True)

    pending_leave_requests = LeaveRequest.query.filter_by(status='Pending').order_by(LeaveRequest.start_date.asc()).all()
    recent_incentives = Incentive.query.order_by(Incentive.id.desc()).limit(20).all()
    employee_search_data = [{'id': e.id, 'name': e.username} for e in employees]

    return render_template(
        'payroll_admin.html',
        selected_month=selected_month,
        employees=employees,
        payroll_rows=payroll_rows,
        pending_leave_requests=pending_leave_requests,
        recent_incentives=recent_incentives,
        name_filter=name_filter,
        salary_sort=salary_sort,
        employee_search_data=employee_search_data,
    )


@payroll_bp.route('/payroll/admin/employee/<int:employee_id>')
@login_required
def payroll_admin_details(employee_id):
    if not is_admin_user(current_user):
        flash('You do not have permission to access this page.')
        return redirect(url_for('payroll.payroll_home'))

    employee = User.query.get_or_404(employee_id)

    month_param = request.args.get('month', '')
    year, month, selected_month = parse_month(month_param)

    totals = monthly_totals(employee.id, year, month)
    breakdown = monthly_breakdown(employee.id, year, month)

    start_date, end_date = month_date_range(year, month)
    incentives = Incentive.query.filter(
        Incentive.employee_id == employee.id,
        Incentive.month == selected_month,
    ).order_by(Incentive.id.desc()).all()

    leave_requests = LeaveRequest.query.filter(
        LeaveRequest.employee_id == employee.id,
        LeaveRequest.start_date <= end_date,
        LeaveRequest.end_date >= start_date,
    ).order_by(LeaveRequest.start_date.asc()).all()

    deductions = SalaryDeduction.query.filter(
        SalaryDeduction.employee_id == employee.id,
        SalaryDeduction.date >= start_date,
        SalaryDeduction.date <= end_date,
    ).order_by(SalaryDeduction.date.asc()).all()

    return render_template(
        'payroll_admin_detail.html',
        employee=employee,
        selected_month=selected_month,
        totals=totals,
        breakdown=breakdown,
        incentives=incentives,
        leave_requests=leave_requests,
        deductions=deductions,
    )


@payroll_bp.route('/payroll/admin/salary', methods=['POST'])
@login_required
def set_salary():
    if not is_admin_user(current_user):
        flash('You do not have permission to perform this action.')
        return redirect(url_for('payroll.payroll_home'))

    employee_id = int(request.form.get('employee_id'))
    yearly_salary = float(request.form.get('yearly_salary') or 0)

    payroll = Payroll.query.filter_by(employee_id=employee_id).first()
    if payroll is None:
        payroll = Payroll(employee_id=employee_id)
        db.session.add(payroll)

    payroll.yearly_salary = yearly_salary
    payroll.daily_salary = round(yearly_salary / days_in_year(date.today().year), 2) if yearly_salary > 0 else 0.0

    db.session.commit()
    flash('Yearly salary updated successfully.')
    return redirect(url_for('payroll.payroll_admin'))


@payroll_bp.route('/payroll/admin/incentive', methods=['POST'])
@login_required
def add_incentive():
    if not is_admin_user(current_user):
        flash('You do not have permission to perform this action.')
        return redirect(url_for('payroll.payroll_home'))

    employee_id = int(request.form.get('employee_id'))
    amount = float(request.form.get('amount') or 0)
    reason = request.form.get('reason', '').strip()
    month = request.form.get('month', '').strip()

    if not month:
        flash('Month is required for incentives.')
        return redirect(url_for('payroll.payroll_admin'))

    db.session.add(Incentive(employee_id=employee_id, amount=amount, reason=reason, month=month))
    db.session.commit()

    flash('Incentive added successfully.')
    return redirect(url_for('payroll.payroll_admin', month=month))


@payroll_bp.route('/payroll/admin/deduction/<int:deduction_id>/reinstate', methods=['POST'])
@login_required
def reinstate_deduction(deduction_id):
    if not is_admin_user(current_user):
        flash('You do not have permission to perform this action.')
        return redirect(url_for('payroll.payroll_home'))

    deduction = SalaryDeduction.query.get_or_404(deduction_id)
    deduction.status = 'REINSTATED'
    db.session.commit()

    flash('Deduction reinstated successfully.')
    return redirect(request.referrer or url_for('payroll.payroll_admin'))


@payroll_bp.route('/payroll/admin/deduction/<int:deduction_id>/keep', methods=['POST'])
@login_required
def keep_deduction(deduction_id):
    if not is_admin_user(current_user):
        flash('You do not have permission to perform this action.')
        return redirect(url_for('payroll.payroll_home'))

    deduction = SalaryDeduction.query.get_or_404(deduction_id)
    deduction.status = 'DEDUCTED'
    db.session.commit()

    flash('Deduction marked as kept.')
    return redirect(request.referrer or url_for('payroll.payroll_admin'))


@payroll_bp.route('/payroll/admin/leave/<int:leave_id>/<action>', methods=['POST'])
@login_required
def update_leave_status(leave_id, action):
    if not is_admin_user(current_user):
        flash('You do not have permission to perform this action.')
        return redirect(url_for('payroll.payroll_home'))

    leave_request = LeaveRequest.query.get_or_404(leave_id)

    if action == 'approve':
        leave_request.status = 'Approved'
        deductions = SalaryDeduction.query.filter(
            SalaryDeduction.employee_id == leave_request.employee_id,
            SalaryDeduction.date >= leave_request.start_date,
            SalaryDeduction.date <= leave_request.end_date,
            SalaryDeduction.status == 'DEDUCTED',
        ).all()
        for deduction in deductions:
            deduction.status = 'REINSTATED'
    elif action == 'reject':
        leave_request.status = 'Rejected'
    else:
        flash('Invalid action.')
        return redirect(url_for('payroll.payroll_admin'))

    db.session.commit()
    flash('Leave request updated.')
    return redirect(request.referrer or url_for('payroll.payroll_admin'))
