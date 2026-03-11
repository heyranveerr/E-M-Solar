from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from functools import wraps
import secrets
import string
from config import Config
from extensions import db
from models.project import SolarProject
from models.material import Material
from models.asset import Asset
from models.finance import FinanceTransaction
from models.purchase_order import PurchaseOrder, PurchaseOrderItem
from models.bbu_item import BBUSupplyItem, BBUServiceItem # Import new models
from models.user import User
from models.crm import CRM
from models.crm_remark import CRMRemark
from models.crm_reminder import CRMReminder
from models.payroll import Payroll, SalaryDeduction, Incentive, LeaveRequest

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route("/login", methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and user.password == password:  # In production, use hashed passwords
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route("/")
    @login_required
    def home():
        # Show pending leave requests for admin users
        if current_user.role == 'admin':
            pending_leaves = LeaveRequest.query.filter_by(status='Pending').all()
            for leave in pending_leaves:
                employee = User.query.get(leave.employee_id)
                date_range = f"{leave.start_date.strftime('%Y-%m-%d')} to {leave.end_date.strftime('%Y-%m-%d')}"
                flash(f"Pending leave from {employee.username} ({date_range}): {leave.subject}", 'info')
        return render_template("home.html")

    def admin_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != 'admin':
                flash('Admin access required.', 'danger')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated

    def generate_password(length=10):
        chars = string.ascii_letters + string.digits
        return ''.join(secrets.choice(chars) for _ in range(length))

    @app.route('/admin/employees')
    @login_required
    @admin_required
    def manage_employees():
        employees = User.query.filter(User.role.notin_(['admin', 'deleted'])).order_by(User.username).all()
        return render_template('manage_employees.html', employees=employees)

    @app.route('/admin/employees/add', methods=['POST'])
    @login_required
    @admin_required
    def add_employee():
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'employee').strip()
        if not username:
            flash('Username is required.', 'danger')
            return redirect(url_for('manage_employees'))
        if User.query.filter_by(username=username).first():
            flash(f'Username "{username}" already exists.', 'danger')
            return redirect(url_for('manage_employees'))
        if not password:
            password = generate_password()
        from datetime import date as _date
        new_user = User(username=username, password=password, role=role, joining_date=_date.today())
        db.session.add(new_user)
        db.session.commit()
        flash(f'Employee "{username}" added. Password: {password}', 'success')
        return redirect(url_for('manage_employees'))

    @app.route('/admin/employees/<int:user_id>/reset_password', methods=['POST'])
    @login_required
    @admin_required
    def reset_employee_password(user_id):
        user = User.query.get_or_404(user_id)
        custom_password = request.form.get('custom_password', '').strip()
        new_password = custom_password if custom_password else generate_password()
        user.password = new_password
        db.session.commit()
        flash(f'Password for "{user.username}" reset to: {new_password}', 'success')
        return redirect(url_for('manage_employees'))

    @app.route('/admin/employees/<int:user_id>/delete', methods=['POST'])
    @login_required
    @admin_required
    def delete_employee(user_id):
        user = User.query.get_or_404(user_id)
        if user.role == 'admin':
            flash('Cannot delete admin accounts.', 'danger')
            return redirect(url_for('manage_employees'))
        username = user.username
        # Preserve username for historical records, only revoke login access
        user.password = ''
        user.role = 'deleted'
        db.session.commit()
        flash(f'Employee "{username}" has been removed. Their historical data is preserved.', 'success')
        return redirect(url_for('manage_employees'))

    from routes.project_routes import project_bp
    app.register_blueprint(project_bp)

    from routes.asset_routes import asset_bp
    app.register_blueprint(asset_bp)

    from routes.finance_routes import finance_bp
    app.register_blueprint(finance_bp)

    from routes.material_routes import material_bp
    app.register_blueprint(material_bp)

    from routes.purchase_order_routes import purchase_order_bp
    app.register_blueprint(purchase_order_bp)

    from routes.crm_routes import crm_bp
    app.register_blueprint(crm_bp)

    from routes.attendance_routes import attendance_bp
    app.register_blueprint(attendance_bp)

    from routes.payroll_routes import payroll_bp
    app.register_blueprint(payroll_bp)

    return app

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
