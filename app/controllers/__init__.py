from flask import Blueprint

# Import all blueprints
from .auth import auth_bp
from .main import main_bp
from .dashboard import dashboard_bp
from .members import members_bp
from .vehicles import vehicles_bp
from .finance import finance_bp
from .reports import reports_bp
from .settings import settings_bp
from .students import students_bp 