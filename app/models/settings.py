from app import db
from datetime import datetime

class Settings(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<Setting {self.key}>'
    
    @classmethod
    def get(cls, key, default=None):
        """Get a setting value by key"""
        setting = cls.query.filter_by(key=key).first()
        if setting is None:
            return default
        return setting.value
    
    @classmethod
    def set(cls, key, value, description=None):
        """Set or update a setting value"""
        setting = cls.query.filter_by(key=key).first()
        if setting is None:
            setting = cls(key=key, value=str(value), description=description)
            db.session.add(setting)
        else:
            setting.value = str(value)
            if description:
                setting.description = description
        db.session.commit()
        return setting
    
    @classmethod
    def get_all(cls):
        """Get all settings as a dictionary"""
        settings = cls.query.all()
        return {setting.key: setting.value for setting in settings}
    
    @classmethod
    def get_value(cls, key, default=None):
        """Get a setting value with type conversion"""
        value = cls.get(key, default)
        if value is None:
            return default
        
        # Try to convert to appropriate type
        if isinstance(value, str):
            if value.lower() in ('true', 'false'):
                return value.lower() == 'true'
            try:
                return int(value)
            except ValueError:
                try:
                    return float(value)
                except ValueError:
                    return value
        return value 