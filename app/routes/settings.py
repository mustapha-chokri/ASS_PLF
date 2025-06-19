from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.routes import settings_bp

@settings_bp.route('/')
@login_required
def index():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    return render_template('settings/index.html', title='الإعدادات العامة')

@settings_bp.route('/users')
@login_required
def users():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    return render_template('settings/users.html', title='إدارة المستخدمين')

@settings_bp.route('/database')
@login_required
def database():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    return render_template('settings/database.html', title='إدارة قاعدة البيانات')

@settings_bp.route('/logs')
@login_required
def logs():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    return render_template('settings/logs.html', title='سجل الأحداث')

@settings_bp.route('/notifications')
@login_required
def notifications():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    return render_template('settings/notifications.html', title='الإشعارات') 