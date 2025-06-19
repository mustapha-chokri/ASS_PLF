from app import db
from datetime import datetime
from flask_login import current_user

class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    national_id = db.Column(db.String(20), unique=True, nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    address = db.Column(db.String(256), nullable=True)
    city = db.Column(db.String(64), nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    profession = db.Column(db.String(64), nullable=True)
    join_date = db.Column(db.Date, default=datetime.now().date, nullable=False)
    status = db.Column(db.String(20), default='active', nullable=False)  # active, inactive, suspended
    photo_path = db.Column(db.String(256), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('Subscription', backref='member', lazy='dynamic')
    
    def __repr__(self):
        return f'<Member {self.first_name} {self.last_name}>'
    
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
class MembershipApplication(db.Model):
    __tablename__ = 'membership_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    national_id = db.Column(db.String(20), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    address = db.Column(db.String(256), nullable=True)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    profession = db.Column(db.String(64), nullable=True)
    application_date = db.Column(db.Date, default=datetime.now().date, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, approved, rejected
    notes = db.Column(db.Text, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    review_date = db.Column(db.DateTime, nullable=True)
    application_token = db.Column(db.String(64), unique=True)
    
    def __repr__(self):
        return f'<MembershipApplication {self.first_name} {self.last_name}>' 