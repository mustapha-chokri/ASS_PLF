from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
finance_bp = Blueprint('finance', __name__, url_prefix='/finance')
students_bp = Blueprint('students', __name__, url_prefix='/students')
settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

from . import admin, finance, students, settings 