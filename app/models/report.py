from datetime import datetime
from app import db

class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # financial, literary
    file_path = db.Column(db.String(255))  # مسار ملف التقرير
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    # العلاقات
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_reports')

    def __init__(self, title, report_type, file_path=None, created_by=None):
        self.title = title
        self.report_type = report_type
        self.file_path = file_path
        self.created_by = created_by
        self.status = 'pending'  # تعيين الحالة الافتراضية

    def __repr__(self):
        return f'<Report {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'report_type': self.report_type,
            'file_path': self.file_path,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }

    def update_status(self, status):
        """تحديث حالة التقرير"""
        self.status = status
        db.session.commit() 