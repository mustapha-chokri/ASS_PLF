from app import db
from datetime import datetime

class Log(db.Model):
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(10), nullable=False, default='info')  # info, warning, error
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقة مع المستخدم
    user = db.relationship('User', backref=db.backref('logs', lazy=True))
    
    @classmethod
    def log(cls, level, message, user_id=None):
        """تسجيل حدث في قاعدة البيانات"""
        try:
            log = cls(level=level, message=message, user_id=user_id)
            db.session.add(log)
            db.session.commit()
            return log
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def info(cls, message, user_id=None):
        """تسجيل حدث معلوماتي"""
        return cls.log('info', message, user_id)
    
    @classmethod
    def warning(cls, message, user_id=None):
        """تسجيل تحذير"""
        return cls.log('warning', message, user_id)
    
    @classmethod
    def error(cls, message, user_id=None):
        """تسجيل خطأ"""
        return cls.log('error', message, user_id)
    
    def __repr__(self):
        return f'<Log {self.level}: {self.message}>' 