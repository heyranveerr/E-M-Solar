from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
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
        return render_template("home.html")

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

    return app

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
