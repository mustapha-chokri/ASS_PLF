from app import db
from datetime import datetime

class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    activity_type = db.Column(db.String(64), nullable=False)  # cultural, social, educational, etc.
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(128), nullable=True)
    budget = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='planned', nullable=False)  # planned, in-progress, completed, cancelled
    responsible_person = db.Column(db.String(128), nullable=True)
    participants_count = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attachments = db.relationship('ActivityAttachment', backref='activity', lazy='dynamic')
    
    def __repr__(self):
        return f'<Activity {self.title}>'

class ActivityAttachment(db.Model):
    __tablename__ = 'activity_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    file_name = db.Column(db.String(128), nullable=False)
    file_path = db.Column(db.String(256), nullable=False)
    file_type = db.Column(db.String(64), nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ActivityAttachment {self.file_name} - Activity {self.activity_id}>'

class Meeting(db.Model):
    __tablename__ = 'meetings'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    meeting_type = db.Column(db.String(64), nullable=False)  # general assembly, board, committee
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(128), nullable=True)
    agenda = db.Column(db.Text, nullable=True)
    minutes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='scheduled', nullable=False)  # scheduled, in-progress, completed, cancelled
    attendees_count = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attachments = db.relationship('MeetingAttachment', backref='meeting', lazy='dynamic')
    attendees = db.relationship('MeetingAttendance', backref='meeting', lazy='dynamic')
    
    def __repr__(self):
        return f'<Meeting {self.title} - {self.date}>'

class MeetingAttachment(db.Model):
    __tablename__ = 'meeting_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'), nullable=False)
    file_name = db.Column(db.String(128), nullable=False)
    file_path = db.Column(db.String(256), nullable=False)
    file_type = db.Column(db.String(64), nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MeetingAttachment {self.file_name} - Meeting {self.meeting_id}>'

class MeetingAttendance(db.Model):
    __tablename__ = 'meeting_attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=True)
    attendee_name = db.Column(db.String(128), nullable=True)  # For non-members
    status = db.Column(db.String(20), default='present', nullable=False)  # present, absent, excused
    notes = db.Column(db.Text, nullable=True)
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        if self.member_id:
            return f'<Attendance Meeting:{self.meeting_id} - Member:{self.member_id}>'
        else:
            return f'<Attendance Meeting:{self.meeting_id} - Name:{self.attendee_name}>' 