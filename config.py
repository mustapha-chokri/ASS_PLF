import os
from datetime import timedelta

# الحصول على المسار المطلق للمجلد الحالي
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration settings for the Flask application"""
    # Secret key for secure sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123'
    
    # CSRF configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = 'your-csrf-secret-key-here'
    
    # Database configuration - استخدام المسار المطلق
    DATABASE_PATH = os.path.join(basedir, "data", "app.db")
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Migrate configuration - استخدام المسار المطلق
    MIGRATIONS_DIR = os.path.join(basedir, 'migrations')
    
    # Upload folder for files - استخدام المسار المطلق
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_TYPE = 'filesystem'
    
    # Default language
    DEFAULT_LANGUAGE = 'ar'
    
    # Maximum content length for file uploads (16MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 

    # إعدادات البريد الإلكتروني
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your-email@gmail.com'
    MAIL_PASSWORD = 'your-app-password'
    MAIL_DEFAULT_SENDER = 'your-email@gmail.com'
    MAIL_RECIPIENTS = ['recipient1@example.com', 'recipient2@example.com']

    # إعدادات WhatsApp
    TWILIO_ACCOUNT_SID = 'your-account-sid'
    TWILIO_AUTH_TOKEN = 'your-auth-token'
    TWILIO_WHATSAPP_NUMBER = '+1234567890'
    WHATSAPP_RECIPIENT = '+1234567890' 