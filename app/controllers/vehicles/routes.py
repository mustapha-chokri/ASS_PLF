from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from app import db
from app.controllers.vehicles import vehicles_bp
from app.models.vehicle import Vehicle, Driver, DriverVehicleAssignment, VehicleMaintenance
from datetime import datetime, date, timedelta
from sqlalchemy import and_
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, FloatField, DateField, TextAreaField, HiddenField, FileField, SubmitField
from wtforms.validators import DataRequired, Optional
import pandas as pd
from app.utils.notifications import send_email, send_whatsapp
import os
from app.forms.vehicle import VehicleForm
from app.forms.vehicle_import import VehicleImportForm
from werkzeug.utils import secure_filename
import io
from app.utils.vehicle_utils import export_vehicles_to_excel, import_vehicles_from_excel, export_vehicles_template
from io import BytesIO

vehicles = Blueprint('vehicles', __name__)

class DriverForm(FlaskForm):
    first_name = StringField('الاسم الأول', validators=[DataRequired()])
    last_name = StringField('الاسم الأخير', validators=[DataRequired()])
    national_id = StringField('رقم الهوية', validators=[DataRequired()])
    license_number = StringField('رقم الرخصة', validators=[DataRequired()])
    license_expiry = DateField('تاريخ انتهاء الرخصة', validators=[DataRequired()])
    birth_date = DateField('تاريخ الميلاد')
    phone = StringField('رقم الهاتف', validators=[DataRequired()])
    email = StringField('البريد الإلكتروني')
    hire_date = DateField('تاريخ التوظيف', validators=[DataRequired()])
    status = SelectField('الحالة', choices=[
        ('active', 'نشط'),
        ('inactive', 'غير نشط'),
        ('suspended', 'معلق')
    ], validators=[DataRequired()])
    address = TextAreaField('العنوان')
    notes = TextAreaField('ملاحظات')

class AssignmentForm(FlaskForm):
    vehicle_id = SelectField('السيارة', coerce=int, validators=[DataRequired()])
    driver_id = SelectField('السائق', coerce=int, validators=[DataRequired()])
    assignment_type = SelectField('نوع المهمة', choices=[
        ('', 'اختر نوع المهمة'),
        ('regular', 'مهمة منتظمة'),
        ('special', 'مهمة خاصة'),
        ('emergency', 'مهمة طارئة')
    ], validators=[DataRequired()])
    status = SelectField('الحالة', choices=[
        ('active', 'نشط'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي')
    ], validators=[DataRequired()])
    start_date = DateField('تاريخ البداية', validators=[DataRequired()])
    end_date = DateField('تاريخ النهاية')
    description = TextAreaField('وصف المهمة')
    notes = TextAreaField('ملاحظات')

class MaintenanceForm(FlaskForm):
    vehicle_id = SelectField('السيارة', coerce=int, validators=[DataRequired()])
    maintenance_type = SelectField('نوع الصيانة', choices=[
        ('', 'اختر نوع الصيانة'),
        ('regular', 'صيانة دورية'),
        ('repair', 'إصلاح'),
        ('emergency', 'صيانة طارئة')
    ], validators=[DataRequired()])
    status = SelectField('الحالة', choices=[
        ('scheduled', 'مجدول'),
        ('in_progress', 'قيد التنفيذ'),
        ('completed', 'مكتمل')
    ], validators=[DataRequired()])
    start_date = DateField('تاريخ البداية', validators=[DataRequired()])
    end_date = DateField('تاريخ النهاية')
    cost = FloatField('التكلفة')
    description = TextAreaField('وصف الصيانة')
    service_provider = StringField('مزود الخدمة')
    notes = TextAreaField('ملاحظات')
    
    # الحقول الجديدة
    maintenance_date = DateField('تاريخ الفيدونج', validators=[DataRequired()])
    current_mileage = IntegerField('الكيلومتراج الحالي', validators=[DataRequired()])
    next_maintenance_mileage = IntegerField('الكيلومتراج الذي ستم فيه الفيدونج القادم')
    maintenance_type = SelectField('نوع الفيدونج', choices=[
        ('', 'اختر نوع الفيدونج'),
        ('regular', 'صيانة دورية'),
        ('repair', 'إصلاح'),
        ('emergency', 'صيانة طارئة')
    ], validators=[DataRequired()])

class FuelForm(FlaskForm):
    vehicle_id = SelectField('السيارة', coerce=int, validators=[DataRequired()])
    date = DateField('التاريخ', validators=[DataRequired()])
    quantity = FloatField('الكمية', validators=[DataRequired()])
    cost = FloatField('التكلفة', validators=[DataRequired()])
    fuel_type = SelectField('نوع الوقود', choices=[
        ('', 'اختر نوع الوقود'),
        ('petrol', 'بنزين'),
        ('diesel', 'ديزل'),
        ('gas', 'غاز')
    ], validators=[DataRequired()])
    station = StringField('محطة الوقود')
    notes = TextAreaField('ملاحظات')

class DeleteVehicleForm(FlaskForm):
    id = HiddenField('ID', validators=[DataRequired()])

@vehicles_bp.route('/')
@login_required
def index():
    """عرض قائمة السيارات"""
    vehicles = Vehicle.query.all()
    return render_template('vehicles/index.html', vehicles=vehicles)

@vehicles_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """إضافة سيارة جديدة"""
    form = VehicleForm()
    if form.validate_on_submit():
        try:
            vehicle = Vehicle(
                registration_number=form.registration_number.data,
                vehicle_type=form.vehicle_type.data,
                brand=form.brand.data,
                model=form.model.data,
                year=form.year.data,
                capacity=form.capacity.data,
                status=form.status.data,
                purchase_price=form.purchase_price.data,
                purchase_date=form.purchase_date.data,
                registration_expiry=form.registration_expiry.data,
                insurance_expiry=form.insurance_expiry.data,
                inspection_expiry=form.inspection_expiry.data,
                driving_license_expiry=form.driving_license_expiry.data,
                current_mileage=form.current_mileage.data,
                next_maintenance_mileage=form.next_maintenance_mileage.data,
                next_maintenance_type=form.next_maintenance_type.data,
                notes=form.notes.data
            )
            db.session.add(vehicle)
            db.session.commit()
            flash('تم إضافة السيارة بنجاح', 'success')
            return redirect(url_for('vehicles.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إضافة السيارة: {str(e)}', 'danger')
    return render_template('vehicles/add.html', form=form)

@vehicles_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """تعديل بيانات سيارة"""
    vehicle = Vehicle.query.get_or_404(id)
    form = VehicleForm(obj=vehicle)
    if form.validate_on_submit():
        form.populate_obj(vehicle)
        db.session.commit()
        flash('تم تحديث بيانات السيارة بنجاح', 'success')
        return redirect(url_for('vehicles.index'))
    return render_template('vehicles/form.html', form=form, title='تعديل بيانات السيارة')

@vehicles_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """حذف سيارة"""
    vehicle = Vehicle.query.get_or_404(id)
    try:
        db.session.delete(vehicle)
        db.session.commit()
        flash('تم حذف السيارة بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف السيارة: {str(e)}', 'danger')
    return redirect(url_for('vehicles.index'))

@vehicles_bp.route('/drivers')
@login_required
def drivers():
    drivers = Driver.query.all()
    return render_template('vehicles/drivers.html', title='إدارة السائقين', drivers=drivers)

@vehicles_bp.route('/drivers/add', methods=['GET', 'POST'])
@login_required
def add_driver():
    form = DriverForm()
    if form.validate_on_submit():
        driver = Driver(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            national_id=form.national_id.data,
            license_number=form.license_number.data,
            license_expiry=form.license_expiry.data,
            birth_date=form.birth_date.data,
            phone=form.phone.data,
            email=form.email.data,
            hire_date=form.hire_date.data,
            status=form.status.data,
            address=form.address.data,
            notes=form.notes.data
        )
        db.session.add(driver)
        db.session.commit()
        flash('تمت إضافة السائق بنجاح!', 'success')
        return redirect(url_for('vehicles.drivers'))
    return render_template('vehicles/add_driver.html', title='إضافة سائق جديد', form=form)

@vehicles_bp.route('/drivers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_driver(id):
    driver = Driver.query.get_or_404(id)
    form = DriverForm(obj=driver)
    if form.validate_on_submit():
        driver.first_name = form.first_name.data
        driver.last_name = form.last_name.data
        driver.national_id = form.national_id.data
        driver.license_number = form.license_number.data
        driver.license_expiry = form.license_expiry.data
        driver.birth_date = form.birth_date.data
        driver.phone = form.phone.data
        driver.email = form.email.data
        driver.hire_date = form.hire_date.data
        driver.status = form.status.data
        driver.address = form.address.data
        driver.notes = form.notes.data
        db.session.commit()
        flash('تم تحديث بيانات السائق بنجاح!', 'success')
        return redirect(url_for('vehicles.drivers'))
    return render_template('vehicles/edit_driver.html', title='تعديل بيانات السائق', form=form, driver=driver)

@vehicles_bp.route('/drivers/delete/<int:id>', methods=['POST'])
@login_required
def delete_driver(id):
    driver = Driver.query.get_or_404(id)
    db.session.delete(driver)
    db.session.commit()
    flash('تم حذف السائق بنجاح!', 'success')
    return redirect(url_for('vehicles.drivers'))

@vehicles_bp.route('/assignments')
@login_required
def assignments():
    assignments = DriverVehicleAssignment.query.all()
    return render_template('vehicles/assignments.html', title='إدارة المهام', assignments=assignments)

@vehicles_bp.route('/assignments/add', methods=['GET', 'POST'])
@login_required
def add_assignment():
    form = AssignmentForm()
    form.vehicle_id.choices = [(v.id, f"{v.registration_number} - {v.brand} {v.model}") for v in Vehicle.query.all()]
    form.driver_id.choices = [(d.id, f"{d.full_name} - {d.license_number}") for d in Driver.query.all()]
    if form.validate_on_submit():
        assignment = DriverVehicleAssignment(
            driver_id=form.driver_id.data,
            vehicle_id=form.vehicle_id.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            notes=form.notes.data,
            created_by=current_user.id
        )
        db.session.add(assignment)
        db.session.commit()
        flash('تمت إضافة المهمة بنجاح!', 'success')
        return redirect(url_for('vehicles.assignments'))
    return render_template('vehicles/add_assignment.html', title='إضافة مهمة جديدة', form=form)

@vehicles_bp.route('/assignments/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_assignment(id):
    assignment = DriverVehicleAssignment.query.get_or_404(id)
    form = AssignmentForm(obj=assignment)
    form.vehicle_id.choices = [(v.id, f"{v.registration_number} - {v.brand} {v.model}") for v in Vehicle.query.all()]
    form.driver_id.choices = [(d.id, f"{d.full_name} - {d.license_number}") for d in Driver.query.all()]
    if form.validate_on_submit():
        assignment.driver_id = form.driver_id.data
        assignment.vehicle_id = form.vehicle_id.data
        assignment.start_date = form.start_date.data
        assignment.end_date = form.end_date.data
        assignment.notes = form.notes.data
        db.session.commit()
        flash('تم تحديث المهمة بنجاح!', 'success')
        return redirect(url_for('vehicles.assignments'))
    return render_template('vehicles/edit_assignment.html', title='تعديل المهمة', form=form, assignment=assignment)

@vehicles_bp.route('/assignments/delete/<int:id>', methods=['POST'])
@login_required
def delete_assignment(id):
    assignment = DriverVehicleAssignment.query.get_or_404(id)
    db.session.delete(assignment)
    db.session.commit()
    flash('تم حذف المهمة بنجاح!', 'success')
    return redirect(url_for('vehicles.assignments'))

@vehicles_bp.route('/maintenance')
@login_required
def maintenance():
    maintenance_records = VehicleMaintenance.query.all()
    return render_template('vehicles/maintenance.html', title='إدارة الصيانة', maintenance_records=maintenance_records)

@vehicles_bp.route('/maintenance/add', methods=['GET', 'POST'])
@login_required
def add_maintenance():
    form = MaintenanceForm()
    form.vehicle_id.choices = [(v.id, f"{v.registration_number} - {v.brand} {v.model}") for v in Vehicle.query.all()]
    if form.validate_on_submit():
        maintenance = VehicleMaintenance(
            vehicle_id=form.vehicle_id.data,
            maintenance_type=form.maintenance_type.data,
            status=form.status.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            cost=form.cost.data,
            description=form.description.data,
            service_provider=form.service_provider.data,
            notes=form.notes.data,
            created_by=current_user.id
        )
        db.session.add(maintenance)
        db.session.commit()
        flash('تمت إضافة الصيانة بنجاح!', 'success')
        return redirect(url_for('vehicles.maintenance'))
    return render_template('vehicles/add_maintenance.html', title='إضافة صيانة جديدة', form=form)

@vehicles_bp.route('/maintenance/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_maintenance(id):
    maintenance = VehicleMaintenance.query.get_or_404(id)
    form = MaintenanceForm(obj=maintenance)
    form.vehicle_id.choices = [(v.id, f"{v.registration_number} - {v.brand} {v.model}") for v in Vehicle.query.all()]
    if form.validate_on_submit():
        maintenance.vehicle_id = form.vehicle_id.data
        maintenance.maintenance_type = form.maintenance_type.data
        maintenance.status = form.status.data
        maintenance.start_date = form.start_date.data
        maintenance.end_date = form.end_date.data
        maintenance.cost = form.cost.data
        maintenance.description = form.description.data
        maintenance.service_provider = form.service_provider.data
        maintenance.notes = form.notes.data
        db.session.commit()
        flash('تم تحديث بيانات الصيانة بنجاح!', 'success')
        return redirect(url_for('vehicles.maintenance'))
    return render_template('vehicles/edit_maintenance.html', title='تعديل بيانات الصيانة', form=form, maintenance=maintenance)

@vehicles_bp.route('/maintenance/delete/<int:id>', methods=['POST'])
@login_required
def delete_maintenance(id):
    maintenance = VehicleMaintenance.query.get_or_404(id)
    db.session.delete(maintenance)
    db.session.commit()
    flash('تم حذف الصيانة بنجاح!', 'success')
    return redirect(url_for('vehicles.maintenance'))

@vehicles_bp.route('/fuel')
@login_required
def fuel():
    return render_template('vehicles/fuel.html', title='إدارة الوقود')

@vehicles_bp.route('/fuel/add', methods=['GET', 'POST'])
@login_required
def add_fuel():
    return render_template('vehicles/add_fuel.html', title='إضافة تزويد وقود جديد')

@vehicles_bp.route('/fuel/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_fuel(id):
    return render_template('vehicles/edit_fuel.html', title='تعديل بيانات تزويد الوقود')

@vehicles_bp.route('/fuel/delete/<int:id>', methods=['POST'])
@login_required
def delete_fuel(id):
    flash('تم حذف تزويد الوقود بنجاح!', 'success')
    return redirect(url_for('vehicles.fuel'))

@vehicles_bp.route('/reports')
@login_required
def reports():
    return render_template('vehicles/reports.html', title='التقارير')

@vehicles_bp.route('/reports/vehicle-status')
@login_required
def vehicle_status_report():
    vehicles = Vehicle.query.all()
    return render_template('vehicles/reports/vehicle_status.html', title='تقرير حالة السيارات', vehicles=vehicles)

@vehicles_bp.route('/reports/driver-status')
@login_required
def driver_status_report():
    drivers = Driver.query.all()
    return render_template('vehicles/reports/driver_status.html', title='تقرير حالة السائقين', drivers=drivers)

@vehicles_bp.route('/reports/assignment')
@login_required
def assignment_report():
    assignments = DriverVehicleAssignment.query.all()
    return render_template('vehicles/reports/assignment.html', title='تقرير المهام', assignments=assignments)

@vehicles_bp.route('/reports/maintenance')
@login_required
def maintenance_report():
    maintenance_records = VehicleMaintenance.query.all()
    return render_template('vehicles/reports/maintenance.html', title='تقرير الصيانة', maintenance_records=maintenance_records)

@vehicles_bp.route('/reports/fuel')
@login_required
def fuel_report():
    return render_template('vehicles/reports/fuel.html', title='تقرير الوقود')

@vehicles_bp.route('/reports/cost')
@login_required
def cost_report():
    maintenance_records = VehicleMaintenance.query.all()
    return render_template('vehicles/reports/cost.html', title='تقرير التكاليف', maintenance_records=maintenance_records)

@vehicles_bp.route('/api/vehicle-status')
@login_required
def vehicle_status():
    active = Vehicle.query.filter_by(status='active').count()
    maintenance = Vehicle.query.filter_by(status='maintenance').count()
    retired = Vehicle.query.filter_by(status='retired').count()
    return jsonify({
        'active': active,
        'maintenance': maintenance,
        'retired': retired
    })

@vehicles_bp.route('/api/driver-status')
@login_required
def driver_status():
    active = Driver.query.filter_by(status='active').count()
    inactive = Driver.query.filter_by(status='inactive').count()
    suspended = Driver.query.filter_by(status='suspended').count()
    return jsonify({
        'active': active,
        'inactive': inactive,
        'suspended': suspended
    })

@vehicles_bp.route('/api/assignment-status')
@login_required
def assignment_status():
    active = DriverVehicleAssignment.query.filter_by(is_active=True).count()
    completed = DriverVehicleAssignment.query.filter_by(is_active=False).count()
    return jsonify({
        'active': active,
        'completed': completed,
        'cancelled': 0
    })

@vehicles_bp.route('/api/maintenance-status')
@login_required
def maintenance_status():
    scheduled = VehicleMaintenance.query.filter_by(status='scheduled').count()
    in_progress = VehicleMaintenance.query.filter_by(status='in_progress').count()
    completed = VehicleMaintenance.query.filter_by(status='completed').count()
    return jsonify({
        'scheduled': scheduled,
        'in_progress': in_progress,
        'completed': completed
    })

@vehicles_bp.route('/api/fuel-statistics')
@login_required
def fuel_statistics():
    return jsonify({
        'total_cost': 0,
        'total_quantity': 0,
        'average_cost': 0
    })

@vehicles_bp.route('/export')
@login_required
def export_vehicles():
    """تصدير السيارات إلى ملف Excel"""
    try:
        # الحصول على جميع السيارات
        vehicles = Vehicle.query.all()
        
        # إنشاء DataFrame
        data = []
        for vehicle in vehicles:
            data.append({
                'رقم التسجيل': vehicle.registration_number,
                'نوع المركبة': vehicle.vehicle_type,
                'العلامة التجارية': vehicle.brand,
                'الموديل': vehicle.model,
                'سنة الصنع': vehicle.year,
                'السعة': vehicle.capacity,
                'الحالة': vehicle.status,
                'سعر الشراء': vehicle.purchase_price,
                'تاريخ الشراء': vehicle.purchase_date.strftime('%Y-%m-%d') if vehicle.purchase_date else None,
                'تاريخ انتهاء التسجيل': vehicle.registration_expiry.strftime('%Y-%m-%d') if vehicle.registration_expiry else None,
                'تاريخ انتهاء التأمين': vehicle.insurance_expiry.strftime('%Y-%m-%d') if vehicle.insurance_expiry else None,
                'تاريخ انتهاء الفحص': vehicle.inspection_expiry.strftime('%Y-%m-%d') if vehicle.inspection_expiry else None,
                'تاريخ انتهاء رخصة القيادة': vehicle.driving_license_expiry.strftime('%Y-%m-%d') if vehicle.driving_license_expiry else None,
                'المسافة المقطوعة': vehicle.current_mileage,
                'المسافة للصيانة القادمة': vehicle.next_maintenance_mileage,
                'نوع الصيانة القادمة': vehicle.next_maintenance_type,
                'ملاحظات': vehicle.notes
            })
        
        df = pd.DataFrame(data)
        
        # إنشاء ملف Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='السيارات', index=False)
            
            # تنسيق الأعمدة
            worksheet = writer.sheets['السيارات']
            for idx, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).apply(len).max(), len(col)) + 2
                worksheet.set_column(idx, idx, max_length)
        
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='vehicles.xlsx'
        )
    except Exception as e:
        flash(f'حدث خطأ أثناء تصدير البيانات: {str(e)}', 'danger')
        return redirect(url_for('vehicles.index'))

@vehicles_bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_vehicles():
    """استيراد سيارات من ملف إكسل"""
    form = VehicleImportForm()
    if form.validate_on_submit():
        file = form.file.data
        success, message = import_vehicles_from_excel(file)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('vehicles.index'))
    return render_template('vehicles/import.html', form=form)

@vehicles_bp.route('/view/<int:id>')
@login_required
def view(id):
    """عرض تفاصيل السيارة"""
    vehicle = Vehicle.query.get_or_404(id)
    return render_template('vehicles/view.html', vehicle=vehicle)

def check_vehicle_licenses():
    """التحقق من تواريخ انتهاء الرخص وإرسال التنبيهات"""
    today = datetime.now().date()
    warning_days = 30  # عدد الأيام قبل انتهاء الرخصة لإرسال التنبيه
    
    vehicles = Vehicle.query.all()
    for vehicle in vehicles:
        # التحقق من رخصة التسجيل
        if vehicle.registration_expiry:
            days_until_expiry = (vehicle.registration_expiry - today).days
            if 0 <= days_until_expiry <= warning_days:
                message = f"تنبيه: رخصة تسجيل السيارة {vehicle.registration_number} ستنتهي خلال {days_until_expiry} يوم"
                send_email("تنبيه انتهاء رخصة تسجيل", message)
                send_whatsapp(message)
        
        # التحقق من التامين
        if vehicle.insurance_expiry:
            days_until_expiry = (vehicle.insurance_expiry - today).days
            if 0 <= days_until_expiry <= warning_days:
                message = f"تنبيه: تأمين السيارة {vehicle.registration_number} سينتهي خلال {days_until_expiry} يوم"
                send_email("تنبيه انتهاء التامين", message)
                send_whatsapp(message)
        
        # التحقق من الفحص التقني
        if vehicle.inspection_expiry:
            days_until_expiry = (vehicle.inspection_expiry - today).days
            if 0 <= days_until_expiry <= warning_days:
                message = f"تنبيه: الفحص التقني للسيارة {vehicle.registration_number} سينتهي خلال {days_until_expiry} يوم"
                send_email("تنبيه انتهاء الفحص التقني", message)
                send_whatsapp(message)
        
        # التحقق من رخصة السير
        if vehicle.driving_license_expiry:
            days_until_expiry = (vehicle.driving_license_expiry - today).days
            if 0 <= days_until_expiry <= warning_days:
                message = f"تنبيه: رخصة سير السيارة {vehicle.registration_number} ستنتهي خلال {days_until_expiry} يوم"
                send_email("تنبيه انتهاء رخصة السير", message)
                send_whatsapp(message)

@vehicles_bp.route('/export/template')
@login_required
def export_template():
    """تصدير نموذج ملف إكسل فارغ"""
    df = export_vehicles_template()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Vehicles', index=False)
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='vehicle_template.xlsx'
    ) 