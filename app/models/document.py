from app import db
from datetime import datetime

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    document_type = db.Column(db.String(64), nullable=False)  # report, memo, invoice, etc.
    file_name = db.Column(db.String(128), nullable=False)
    file_path = db.Column(db.String(256), nullable=False)
    file_type = db.Column(db.String(64), nullable=True)  # pdf, docx, etc.
    description = db.Column(db.Text, nullable=True)
    tags = db.Column(db.String(256), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Document {self.title}>'

class Correspondence(db.Model):
    __tablename__ = 'correspondence'
    
    id = db.Column(db.Integer, primary_key=True)
    reference_number = db.Column(db.String(64), nullable=True)
    title = db.Column(db.String(128), nullable=False)
    correspondence_type = db.Column(db.String(20), nullable=False)  # incoming, outgoing
    sender = db.Column(db.String(128), nullable=False)
    recipient = db.Column(db.String(128), nullable=False)
    date_received = db.Column(db.Date, nullable=True)
    date_sent = db.Column(db.Date, nullable=True)
    subject = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), default='normal', nullable=False)  # high, normal, low
    status = db.Column(db.String(20), default='received', nullable=False)  # received, processed, replied, archived
    file_path = db.Column(db.String(256), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Correspondence {self.reference_number} - {self.title}>'

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    report_type = db.Column(db.String(64), nullable=False)  # administrative, financial, activity
    period_start = db.Column(db.Date, nullable=True)
    period_end = db.Column(db.Date, nullable=True)
    content = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(256), nullable=True)
    status = db.Column(db.String(20), default='draft', nullable=False)  # draft, finalized, approved, published
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approval_date = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Report {self.title}>'

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(64), unique=True, nullable=False)
    invoice_type = db.Column(db.String(20), nullable=False)  # invoice, receipt
    related_to = db.Column(db.String(64), nullable=True)  # expense, income, etc.
    related_id = db.Column(db.Integer, nullable=True)
    title = db.Column(db.String(128), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    issued_date = db.Column(db.Date, default=datetime.now().date, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='draft', nullable=False)  # draft, issued, paid, cancelled
    payment_date = db.Column(db.Date, nullable=True)
    file_path = db.Column(db.String(256), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>' 