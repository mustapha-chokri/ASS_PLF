from app import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # info, warning, error, success
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Notification {self.id} - {self.title}>'
    
    @classmethod
    def create(cls, user_id, title, message, type='info'):
        """Create a new notification"""
        notification = cls(
            user_id=user_id,
            title=title,
            message=message,
            type=type
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
            db.session.commit()
    
    @classmethod
    def get_unread(cls, user_id):
        """Get all unread notifications for a user"""
        return cls.query.filter_by(user_id=user_id, is_read=False).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_all(cls, user_id, limit=10):
        """Get all notifications for a user"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).limit(limit).all() 