from app import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, default=datetime.now().date, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # cash, bank transfer, etc.
    receipt_number = db.Column(db.String(64), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, completed, failed, refunded
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payment {self.id} - Member {self.member_id} - Amount {self.amount}>'
    
    @classmethod
    def create(cls, member_id, amount, payment_method, description=None, created_by=None):
        """Create a new payment"""
        payment = cls(
            member_id=member_id,
            amount=amount,
            payment_method=payment_method,
            description=description,
            created_by=created_by
        )
        db.session.add(payment)
        db.session.commit()
        return payment
    
    def mark_as_completed(self):
        """Mark payment as completed"""
        if self.status == 'pending':
            self.status = 'completed'
            db.session.commit()
    
    def mark_as_failed(self):
        """Mark payment as failed"""
        if self.status == 'pending':
            self.status = 'failed'
            db.session.commit()
    
    def refund(self):
        """Refund the payment"""
        if self.status == 'completed':
            self.status = 'refunded'
            db.session.commit()
    
    @classmethod
    def get_by_member(cls, member_id):
        """Get all payments for a member"""
        return cls.query.filter_by(member_id=member_id).order_by(cls.payment_date.desc()).all()
    
    @classmethod
    def get_pending(cls):
        """Get all pending payments"""
        return cls.query.filter_by(status='pending').order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_completed(cls):
        """Get all completed payments"""
        return cls.query.filter_by(status='completed').order_by(cls.payment_date.desc()).all() 