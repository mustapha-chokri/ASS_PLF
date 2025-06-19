from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.auth import auth_bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models.user import User
from werkzeug.urls import url_parse
from app.auth.security import check_login_attempts, record_failed_login, reset_failed_login, log_login_attempt

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        ip_address = request.remote_addr
        
        if not check_login_attempts(username, ip_address):
            flash('تم تجاوز الحد الأقصى لمحاولات تسجيل الدخول. الرجاء المحاولة بعد 15 دقيقة', 'danger')
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(form.password.data):
            record_failed_login(username, ip_address)
            log_login_attempt(username, False, ip_address)
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
            return redirect(url_for('auth.login'))
        
        reset_failed_login(username, ip_address)
        log_login_attempt(username, True, ip_address)
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='تسجيل الدخول', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if not current_user.is_admin:
        flash('فقط المشرفين يمكنهم إضافة مستخدمين جدد', 'warning')
        return redirect(url_for('dashboard.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            is_admin=form.is_admin.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('تم تسجيل المستخدم الجديد بنجاح', 'success')
        return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html', title='تسجيل مستخدم جديد', form=form) 