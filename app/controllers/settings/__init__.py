from flask import Blueprint

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

from . import routes 