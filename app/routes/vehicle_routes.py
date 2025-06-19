from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from app.models.vehicle import Vehicle, VehicleType, VehicleStatus, VehicleMaintenance
from app.utils.vehicle_utils import export_vehicles_to_excel, import_vehicles_from_excel
from app import db
from datetime import datetime

bp = Blueprint('vehicles', __name__)

@bp.route('/vehicles')
def index():
    vehicles = Vehicle.query.all()
    return render_template('vehicles/index.html', vehicles=vehicles)

@bp.route('/vehicles/export')
def export_vehicles():
    """تصدير بيانات المركبات إلى ملف إكسل"""
    try:
        output = export_vehicles_to_excel()
        if output:
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'vehicles_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            )
        flash('حدث خطأ أثناء تصدير البيانات', 'error')
        return redirect(url_for('vehicles.index'))
    except Exception as e:
        flash(f'حدث خطأ: {str(e)}', 'error')
        return redirect(url_for('vehicles.index'))

@bp.route('/vehicles/import', methods=['GET', 'POST'])
def import_vehicles():
    """استيراد بيانات المركبات من ملف إكسل"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('لم يتم اختيار ملف', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('لم يتم اختيار ملف', 'error')
            return redirect(request.url)
        
        if not file.filename.endswith('.xlsx'):
            flash('يجب أن يكون الملف بصيغة Excel (.xlsx)', 'error')
            return redirect(request.url)
        
        try:
            if import_vehicles_from_excel(file):
                flash('تم استيراد البيانات بنجاح', 'success')
            else:
                flash('حدث خطأ أثناء استيراد البيانات', 'error')
        except Exception as e:
            flash(f'حدث خطأ: {str(e)}', 'error')
        
        return redirect(url_for('vehicles.index'))
    
    return render_template('vehicles/import.html') 