from app import db
from datetime import datetime

class LiteraryActivity(db.Model):
    __tablename__ = 'literary_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    activity_type = db.Column(db.String(50), nullable=False)  # workshop, seminar, competition, etc.
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(128), nullable=True)
    max_participants = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default='upcoming', nullable=False)  # upcoming, ongoing, completed, cancelled
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    participants = db.relationship('User', secondary='activity_participants', backref='participated_activities')
    
    def __repr__(self):
        return f'<LiteraryActivity {self.title}>'
    
    @classmethod
    def create(cls, title, description, activity_type, start_date, end_date, location=None, max_participants=None, created_by=None):
        """Create a new literary activity"""
        activity = cls(
            title=title,
            description=description,
            activity_type=activity_type,
            start_date=start_date,
            end_date=end_date,
            location=location,
            max_participants=max_participants,
            created_by=created_by
        )
        db.session.add(activity)
        db.session.commit()
        return activity
    
    def update_status(self, status):
        """Update activity status"""
        self.status = status
        db.session.commit()
    
    def add_participant(self, user):
        """Add a participant to the activity"""
        if user not in self.participants:
            if not self.max_participants or len(self.participants) < self.max_participants:
                self.participants.append(user)
                db.session.commit()
                return True
        return False
    
    def remove_participant(self, user):
        """Remove a participant from the activity"""
        if user in self.participants:
            self.participants.remove(user)
            db.session.commit()
            return True
        return False
    
    @classmethod
    def get_upcoming(cls):
        """Get all upcoming activities"""
        return cls.query.filter_by(status='upcoming').order_by(cls.start_date).all()
    
    @classmethod
    def get_ongoing(cls):
        """Get all ongoing activities"""
        return cls.query.filter_by(status='ongoing').order_by(cls.start_date).all()
    
    @classmethod
    def get_completed(cls):
        """Get all completed activities"""
        return cls.query.filter_by(status='completed').order_by(cls.end_date.desc()).all()
    
    @classmethod
    def get_by_type(cls, activity_type):
        """Get all activities of a specific type"""
        return cls.query.filter_by(activity_type=activity_type).order_by(cls.start_date.desc()).all()

# جدول العلاقة بين الأنشطة والمشاركين
activity_participants = db.Table('activity_participants',
    db.Column('activity_id', db.Integer, db.ForeignKey('literary_activities.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
) 