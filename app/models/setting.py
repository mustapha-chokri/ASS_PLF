from app import db
from datetime import datetime

class Setting(db.Model):
    """نموذج إعدادات الجمعية"""
    __tablename__ = 'settings'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    association_name = db.Column(db.String(100), nullable=False)
    logo_path = db.Column(db.String(255))
    description = db.Column(db.Text)
    address = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    website = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Setting {self.association_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'association_name': self.association_name,
            'logo_path': self.logo_path,
            'description': self.description,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        } 