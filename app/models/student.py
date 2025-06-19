from app import db
from datetime import datetime
import secrets

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)  # Manual ID entry, must be unique
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=True)  # male/female (ذكر/أنثى)
    massar_number = db.Column(db.String(100), nullable=True)  # National educational ID
    birth_date = db.Column(db.Date, nullable=True)
    educational_level = db.Column(db.String(100), nullable=True)
    institution = db.Column(db.String(100), nullable=True)
    monthly_fee = db.Column(db.Float, default=0)
    
    # Guardian information
    guardian_name = db.Column(db.String(100), nullable=True)
    guardian_national_id = db.Column(db.String(100), nullable=True)
    guardian_phone = db.Column(db.String(20), nullable=True)
    guardian_email = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    
    # Media files
    student_photo = db.Column(db.String(255), nullable=True)
    guardian_id_front = db.Column(db.String(255), nullable=True)
    guardian_id_back = db.Column(db.String(255), nullable=True)
    commitment_doc = db.Column(db.String(255), nullable=True)
    
    # Blacklist information
    is_blacklisted = db.Column(db.Boolean, default=False)
    blacklist_reason = db.Column(db.Text, nullable=True)
    blacklist_duration = db.Column(db.Integer, nullable=True)  # Duration in days
    blacklist_start_date = db.Column(db.Date, nullable=True)
    blacklist_end_date = db.Column(db.Date, nullable=True)
    
    notes = db.Column(db.Text, nullable=True)
    registration_date = db.Column(db.Date, default=datetime.now().date())
    status = db.Column(db.String(20), default='active')  # active, inactive
    
    # Relationships
    transport_subscriptions = db.relationship('TransportSubscription', backref='student', lazy=True)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Student {self.student_id}: {self.full_name}>"


class TransportSubscription(db.Model):
    __tablename__ = 'transport_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, default=datetime.now().date())
    payment_method = db.Column(db.String(50), nullable=True)
    receipt_number = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f"<TransportSubscription {self.id}: {self.month}/{self.year}>"


class EducationalLevel(db.Model):
    __tablename__ = 'educational_levels'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    order = db.Column(db.Integer, default=0)  # For sorting
    description = db.Column(db.Text, nullable=True)  # Description field
    
    def __repr__(self):
        return f"<EducationalLevel {self.name}>"


class Program(db.Model):
    __tablename__ = 'programs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    max_capacity = db.Column(db.Integer, nullable=True)
    fee = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='active', nullable=False)  # planned, active, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('StudentEnrollment', backref='program', lazy='dynamic')
    
    def __repr__(self):
        return f'<Program {self.name}>'


class StudentEnrollment(db.Model):
    __tablename__ = 'student_enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    enrollment_date = db.Column(db.Date, default=datetime.now().date, nullable=False)
    fee_paid = db.Column(db.Float, default=0, nullable=False)
    payment_status = db.Column(db.String(20), default='pending', nullable=False)  # pending, partial, paid, waived
    status = db.Column(db.String(20), default='active', nullable=False)  # active, completed, dropped
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Enrollment Student:{self.student_id} - Program:{self.program_id}>'


class PendingStudent(db.Model):
    __tablename__ = 'pending_students'
    
    id = db.Column(db.Integer, primary_key=True)
    registration_token = db.Column(db.String(50), unique=True, nullable=False)
    
    # Student information
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    massar_number = db.Column(db.String(100), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    educational_level = db.Column(db.String(100), nullable=True)
    institution = db.Column(db.String(100), nullable=True)
    
    # Guardian information
    guardian_name = db.Column(db.String(100), nullable=True)
    guardian_national_id = db.Column(db.String(100), nullable=True)
    guardian_phone = db.Column(db.String(20), nullable=True)  # Changed to nullable=True
    guardian_email = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    
    # Temp file storage paths
    student_photo = db.Column(db.String(255), nullable=True)
    guardian_id_front = db.Column(db.String(255), nullable=True)
    guardian_id_back = db.Column(db.String(255), nullable=True)
    commitment_doc = db.Column(db.String(255), nullable=True)
    
    notes = db.Column(db.Text, nullable=True)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    admin_notes = db.Column(db.Text, nullable=True)  # Notes from admin during review
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return "غير معروف"
    
    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(16)
    
    def __repr__(self):
        return f"<PendingStudent {self.id}: {self.full_name}>" 