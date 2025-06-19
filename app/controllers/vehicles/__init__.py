from flask import Blueprint

vehicles_bp = Blueprint('vehicles', __name__, url_prefix='/vehicles')

# استيراد المسارات بعد تعريف Blueprint
from . import routes 