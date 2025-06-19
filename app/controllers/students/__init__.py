from flask import Blueprint

students_bp = Blueprint('students', __name__, url_prefix='/students')

from app.controllers.students import routes 