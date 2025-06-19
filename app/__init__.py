import os
from flask import Flask, redirect, url_for, render_template, session, flash, request, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect
from config import Config
import jinja2
import markupsafe
from markupsafe import Markup
from datetime import datetime, timedelta
from flask_login import current_user, logout_user
import logging

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bootstrap = Bootstrap()
moment = Moment()
csrf = CSRFProtect()

# Configure login manager
login_manager.login_view = 'auth.login'
login_manager.login_message = 'الرجاء تسجيل الدخول للوصول إلى هذه الصفحة'
login_manager.login_message_category = 'info'
login_manager.session_protection = 'strong'

# Import models
from app.models.finance import (
    Income, IncomeSource,
    Expense, ExpenseType,
    CashBox, BankAccount, Transfer
)
from app.models.user import User
from app.models.student import Student, TransportSubscription, EducationalLevel, Program, StudentEnrollment, PendingStudent
from app.models.about import About

def nl2br(value):
    """Convert newlines to <br> tags"""
    if not value:
        return ""
    result = markupsafe.escape(value)
    result = result.replace('\n', markupsafe.Markup('<br>\n'))
    return markupsafe.Markup(result)

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # تكوين التطبيق
    app.config.from_object(config_class)
    
    # استخدام المسارات المطلقة من الإعدادات
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = config_class.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = config_class.UPLOAD_FOLDER
    
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Register nl2br filter
    @app.template_filter('nl2br')
    def nl2br(value):
        if value:
            return Markup(value.replace('\n', '<br>'))
        return ''

    # إضافة فلتر format_currency
    @app.template_filter('format_currency')
    def format_currency(value):
        try:
            return f"{float(value):,.2f} دم"
        except (ValueError, TypeError):
            return "0.00 دم"

    # Register CLI command for db migration
    @app.cli.command("init-db")
    def init_db_command():
        """Clear the existing data and create new tables."""
        db.create_all()
        print("Initialized the database.")
    
    # Add command to create admin user
    @app.cli.command("create-admin")
    def create_admin_command():
        """Create an admin user."""
        try:
            admin = User(
                username='admin',
                email='admin@example.com',
                full_name='مدير النظام',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        except Exception as e:
            print(f"Error creating admin user: {str(e)}")
            db.session.rollback()
    
    # Add CSRF token to all templates
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)
    
    # Root route
    @app.route('/')
    def index():
        return redirect(url_for('dashboard.index'))
    
    # Register blueprints
    from app.controllers import (
        auth_bp, main_bp, dashboard_bp, members_bp,
        vehicles_bp, finance_bp, reports_bp, settings_bp,
        students_bp
    )
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(students_bp)
    
    # Initialize scheduler
    with app.app_context():
        from app.utils.scheduler import init_scheduler
        init_scheduler(app)
    
    # Exempt all GET requests from CSRF protection
    @csrf.exempt
    def csrf_exempt_get():
        if request.method == 'GET':
            return True
        return False
    
    # Import models after db is initialized
    from app import models
    
    # إنشاء مجلد التحميلات إذا لم يكن موجوداً
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    with app.app_context():
        # Set up session expired error handler
        @app.before_request
        def check_session_expiry():
            if current_user.is_authenticated and request.endpoint not in ('auth.logout', 'static', None):
                expiry_time = timedelta(hours=24)
                last_seen = session.get('last_seen', None)
                
                if last_seen is None:
                    session['last_seen'] = datetime.utcnow().timestamp()
                else:
                    last_time = datetime.fromtimestamp(last_seen)
                    if datetime.utcnow() - last_time > expiry_time:
                        logout_user()
                        flash('انتهت صلاحية جلستك. الرجاء تسجيل الدخول مرة أخرى.', 'warning')
                        return redirect(url_for('auth.login'))
                    session['last_seen'] = datetime.utcnow().timestamp()
        
        @app.context_processor
        def inject_now():
            return {'now': datetime.now()}
    
    @app.context_processor
    def inject_about():
        about = About.query.first()
        return dict(about=about)
    
    return app 