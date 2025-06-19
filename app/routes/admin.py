from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.routes import admin_bp
from app.utils.backup import create_backup, restore_backup
import os
from datetime import datetime

@admin_bp.route('/backup')
@login_required
def backup():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    backup_dir = os.path.join(current_app.root_path, 'backups')
    backups = []
    
    if os.path.exists(backup_dir):
        for file in os.listdir(backup_dir):
            if file.startswith('backup_') and file.endswith('.db'):
                file_path = os.path.join(backup_dir, file)
                file_stat = os.stat(file_path)
                backups.append({
                    'filename': file,
                    'path': file_path,
                    'date': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
    
    backups.sort(key=lambda x: x['date'], reverse=True)
    return render_template('admin/backup.html', backups=backups)

@admin_bp.route('/backup/create', methods=['POST'])
@login_required
def create_backup_route():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    success, message = create_backup()
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('admin.backup'))

@admin_bp.route('/backup/restore', methods=['POST'])
@login_required
def restore_backup_route():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    backup_file = request.form.get('backup_file')
    if not backup_file:
        flash('لم يتم تحديد ملف النسخة الاحتياطية', 'danger')
        return redirect(url_for('admin.backup'))
    
    success, message = restore_backup(backup_file)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('admin.backup'))

@admin_bp.route('/backup/delete', methods=['POST'])
@login_required
def delete_backup():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    backup_file = request.form.get('backup_file')
    if not backup_file:
        flash('لم يتم تحديد ملف النسخة الاحتياطية', 'danger')
        return redirect(url_for('admin.backup'))
    
    try:
        os.remove(backup_file)
        flash('تم حذف النسخة الاحتياطية بنجاح', 'success')
    except Exception as e:
        flash(f'حدث خطأ أثناء حذف النسخة الاحتياطية: {str(e)}', 'danger')
    
    return redirect(url_for('admin.backup')) 