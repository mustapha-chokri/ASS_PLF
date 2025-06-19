from datetime import datetime, timedelta
from flask import request, session
from functools import wraps
import re

# قاموس لتخزين محاولات تسجيل الدخول الفاشلة
failed_login_attempts = {}

def is_password_strong(password):
    """
    التحقق من قوة كلمة المرور
    """
    if len(password) < 6:  # تم تخفيض الحد الأدنى إلى 6 أحرف
        return False
    return True  # تم إزالة باقي المتطلبات

def check_login_attempts(username, ip_address):
    """
    التحقق من محاولات تسجيل الدخول الفاشلة
    """
    key = f"{username}_{ip_address}"
    if key in failed_login_attempts:
        attempts, last_attempt = failed_login_attempts[key]
        if attempts >= 5 and datetime.now() - last_attempt < timedelta(minutes=15):
            return False
        if datetime.now() - last_attempt > timedelta(minutes=15):
            failed_login_attempts[key] = (0, datetime.now())
    return True

def record_failed_login(username, ip_address):
    """
    تسجيل محاولة تسجيل دخول فاشلة
    """
    key = f"{username}_{ip_address}"
    if key in failed_login_attempts:
        attempts, _ = failed_login_attempts[key]
        failed_login_attempts[key] = (attempts + 1, datetime.now())
    else:
        failed_login_attempts[key] = (1, datetime.now())

def reset_failed_login(username, ip_address):
    """
    إعادة تعيين محاولات تسجيل الدخول الفاشلة
    """
    key = f"{username}_{ip_address}"
    if key in failed_login_attempts:
        del failed_login_attempts[key]

def log_login_attempt(username, success, ip_address):
    """
    تسجيل محاولة تسجيل الدخول
    """
    from app.models import LoginLog
    from app import db
    
    log = LoginLog(
        username=username,
        success=success,
        ip_address=ip_address,
        timestamp=datetime.now()
    )
    db.session.add(log)
    db.session.commit() 