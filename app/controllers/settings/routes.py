from flask import render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from app.controllers.settings import settings_bp
from app.controllers.settings.forms import UserForm, NotificationForm, SettingForm
from app.models.settings import Settings
from app.models.user import User
from app import db
import os
import shutil
from datetime import datetime
from app.models.log import Log
from werkzeug.utils import secure_filename
from app.models.setting import Setting

class SettingsForm(FlaskForm):
    pass

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """عرض إعدادات الجمعية"""
    setting = Setting.query.first()
    form = SettingForm(obj=setting) if setting else SettingForm()
    return render_template('settings/index.html', form=form, setting=setting)

@settings_bp.route('/update', methods=['POST'])
@login_required
def update():
    """تحديث إعدادات الجمعية"""
    setting = Setting.query.first()
    form = SettingForm(obj=setting) if setting else SettingForm()
    
    if form.validate_on_submit():
        try:
            if not setting:
                setting = Setting()
            
            # تحديث البيانات الأساسية
            setting.association_name = form.association_name.data
            setting.description = form.description.data
            setting.address = form.address.data
            setting.phone = form.phone.data
            setting.email = form.email.data
            setting.website = form.website.data
            
            # معالجة الشعار
            if form.logo.data:
                # حذف الشعار القديم إذا وجد
                if setting.logo_path and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], setting.logo_path)):
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], setting.logo_path))
                
                # حفظ الشعار الجديد
                filename = secure_filename(form.logo.data.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                form.logo.data.save(file_path)
                setting.logo_path = filename
            
            if not setting.id:
                db.session.add(setting)
            
            db.session.commit()
            flash('تم تحديث إعدادات الجمعية بنجاح', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء تحديث الإعدادات: {str(e)}', 'danger')
    
    return redirect(url_for('settings.index'))

@settings_bp.route('/update_general', methods=['POST'])
@login_required
def update_general():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    Settings.set('site_name', request.form.get('site_name'), 'اسم الموقع')
    Settings.set('site_description', request.form.get('site_description'), 'وصف الموقع')
    
    flash('تم تحديث الإعدادات العامة بنجاح', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/update_email', methods=['POST'])
@login_required
def update_email():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    Settings.set('smtp_server', request.form.get('smtp_server'), 'خادم SMTP')
    Settings.set('smtp_port', request.form.get('smtp_port'), 'منفذ SMTP')
    Settings.set('smtp_username', request.form.get('smtp_username'), 'اسم مستخدم SMTP')
    
    if request.form.get('smtp_password'):
        Settings.set('smtp_password', request.form.get('smtp_password'), 'كلمة مرور SMTP')
    
    flash('تم تحديث إعدادات البريد الإلكتروني بنجاح', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/users')
@login_required
def users():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    return render_template('settings/users.html', title='إدارة المستخدمين', users=users)

@settings_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    form = UserForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                full_name=form.full_name.data,
                is_admin=form.is_admin.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('تم إضافة المستخدم بنجاح.', 'success')
            return redirect(url_for('settings.users'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'فشل في إضافة المستخدم: {str(e)}')
            flash('فشل في إضافة المستخدم.', 'danger')
    
    return render_template('settings/add_user.html', form=form)

@settings_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    user = User.query.get_or_404(id)
    form = UserForm(obj=user, original_username=user.username, original_email=user.email)
    
    if form.validate_on_submit():
        # Check if username or email already exists (excluding current user)
        if form.username.data != user.username and User.query.filter_by(username=form.username.data).first():
            flash('اسم المستخدم موجود بالفعل.', 'danger')
            return render_template('settings/edit_user.html', form=form, user=user)
        
        if form.email.data != user.email and User.query.filter_by(email=form.email.data).first():
            flash('البريد الإلكتروني موجود بالفعل.', 'danger')
            return render_template('settings/edit_user.html', form=form, user=user)
        
        # Update user with full_name
        user.username = form.username.data
        user.email = form.email.data
        user.full_name = form.full_name.data  # Add full_name field
        user.is_admin = form.is_admin.data
        
        if form.password.data:
            user.set_password(form.password.data)
        
        db.session.commit()
        flash('تم تحديث المستخدم بنجاح.', 'success')
        return redirect(url_for('settings.users'))
    
    return render_template('settings/edit_user.html', form=form, user=user)

@settings_bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
def delete_user(id):
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('لا يمكنك حذف حسابك الخاص', 'danger')
        return redirect(url_for('settings.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('تم حذف المستخدم بنجاح', 'success')
    return redirect(url_for('settings.users'))

@settings_bp.route('/database')
@login_required
def database():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # معلومات قاعدة البيانات
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    db_size = os.path.getsize(db_path) / (1024 * 1024)  # حجم الملف بالميجابايت
    db_info = {
        'size': f'{db_size:.2f} MB',
        'tables': len(db.metadata.tables),
        'last_update': datetime.fromtimestamp(os.path.getmtime(db_path)).strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # قائمة النسخ الاحتياطية
    backup_dir = os.path.join(current_app.root_path, '..', 'backups')
    backups = []
    if os.path.exists(backup_dir):
        for filename in os.listdir(backup_dir):
            if filename.endswith('.db'):
                file_path = os.path.join(backup_dir, filename)
                backups.append({
                    'filename': filename,
                    'date': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                })
    
    # ترتيب النسخ الاحتياطية من الأحدث إلى الأقدم
    backups.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('settings/database.html', db_info=db_info, backups=backups)

@settings_bp.route('/database/backup', methods=['POST'])
@login_required
def backup_database():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    try:
        # إنشاء مجلد النسخ الاحتياطية إذا لم يكن موجوداً
        backup_dir = os.path.join(current_app.root_path, '..', 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # إنشاء اسم ملف النسخة الاحتياطية
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'backup_{timestamp}.db')
        
        # نسخ قاعدة البيانات
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        shutil.copy2(db_path, backup_file)
        
        # تسجيل الحدث
        try:
            Log.info(f'تم إنشاء نسخة احتياطية: {backup_file}', current_user.id)
        except Exception as log_error:
            current_app.logger.error(f'فشل في تسجيل الحدث: {str(log_error)}')
        
        flash('تم إنشاء النسخة الاحتياطية بنجاح.', 'success')
    except Exception as e:
        current_app.logger.error(f'فشل في إنشاء نسخة احتياطية: {str(e)}')
        flash('فشل في إنشاء النسخة الاحتياطية.', 'danger')
    
    return redirect(url_for('settings.database'))

@settings_bp.route('/database/backup/download/<filename>')
@login_required
def download_backup(filename):
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    try:
        backup_dir = os.path.join(current_app.root_path, '..', 'backups')
        backup_file = os.path.join(backup_dir, filename)
        
        if not os.path.exists(backup_file):
            flash('النسخة الاحتياطية غير موجودة.', 'danger')
            return redirect(url_for('settings.database'))
        
        # تسجيل الحدث
        try:
            Log.info(f'تم تحميل نسخة احتياطية: {backup_file}', current_user.id)
        except Exception as log_error:
            db.session.rollback()
            current_app.logger.error(f'فشل في تسجيل الحدث: {str(log_error)}')
        
        return send_file(backup_file, as_attachment=True)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'فشل في تحميل النسخة الاحتياطية: {str(e)}')
        flash('فشل في تحميل النسخة الاحتياطية.', 'danger')
        return redirect(url_for('settings.database'))

@settings_bp.route('/logs')
@login_required
def logs():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    try:
        logs = Log.query.order_by(Log.created_at.desc()).all()
        return render_template('settings/logs.html', logs=logs)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'فشل في عرض سجل الأحداث: {str(e)}')
        flash('فشل في عرض سجل الأحداث.', 'danger')
        return redirect(url_for('settings.index'))

@settings_bp.route('/notifications', methods=['GET', 'POST'])
@login_required
def notifications():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    form = NotificationForm()
    if form.validate_on_submit():
        try:
            # حفظ إعدادات الإشعارات
            Settings.set('email_notifications', form.email_notifications.data)
            Settings.set('sms_notifications', form.sms_notifications.data)
            Settings.set('notification_sound', form.notification_sound.data)
            Settings.set('notification_desktop', form.notification_desktop.data)
            Settings.set('notification_email', form.notification_email.data)
            Settings.set('notification_sms', form.notification_sms.data)
            
            flash('تم حفظ إعدادات الإشعارات بنجاح.', 'success')
            return redirect(url_for('settings.notifications'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'فشل في حفظ إعدادات الإشعارات: {str(e)}')
            flash('فشل في حفظ إعدادات الإشعارات.', 'danger')
    else:
        # تعبئة النموذج بالقيم الحالية
        form.email_notifications.data = Settings.get_value('email_notifications', False)
        form.sms_notifications.data = Settings.get_value('sms_notifications', False)
        form.notification_sound.data = Settings.get_value('notification_sound', True)
        form.notification_desktop.data = Settings.get_value('notification_desktop', True)
        form.notification_email.data = Settings.get_value('notification_email', '')
        form.notification_sms.data = Settings.get_value('notification_sms', '')
    
    return render_template('settings/notifications.html', form=form) 