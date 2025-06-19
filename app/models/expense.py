from app import db
from datetime import datetime

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    expense_date = db.Column(db.Date, default=datetime.now().date, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # cash, bank transfer, etc.
    receipt_number = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Expense {self.id} - {self.category} - Amount {self.amount}>'
    
    @classmethod
    def create(cls, category, amount, description=None, payment_method='cash', created_by=None):
        """Create a new expense"""
        expense = cls(
            category=category,
            amount=amount,
            description=description,
            payment_method=payment_method,
            created_by=created_by
        )
        db.session.add(expense)
        db.session.commit()
        return expense
    
    def approve(self, approved_by):
        """Approve the expense"""
        if self.status == 'pending':
            self.status = 'approved'
            self.approved_by = approved_by
            self.approved_at = datetime.utcnow()
            db.session.commit()
    
    def reject(self):
        """Reject the expense"""
        if self.status == 'pending':
            self.status = 'rejected'
            db.session.commit()
    
    @classmethod
    def get_by_category(cls, category):
        """Get all expenses for a category"""
        return cls.query.filter_by(category=category).order_by(cls.expense_date.desc()).all()
    
    @classmethod
    def get_pending(cls):
        """Get all pending expenses"""
        return cls.query.filter_by(status='pending').order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_approved(cls):
        """Get all approved expenses"""
        return cls.query.filter_by(status='approved').order_by(cls.expense_date.desc()).all()
    
    @classmethod
    def get_total_by_category(cls, category, start_date=None, end_date=None):
        """Get total expenses for a category within a date range"""
        query = cls.query.filter_by(category=category, status='approved')
        if start_date:
            query = query.filter(cls.expense_date >= start_date)
        if end_date:
            query = query.filter(cls.expense_date <= end_date)
        return query.with_entities(db.func.sum(cls.amount)).scalar() or 0 