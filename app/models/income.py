from app import db
from datetime import datetime

class Income(db.Model):
    __tablename__ = 'incomes'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    income_date = db.Column(db.Date, default=datetime.now().date, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # cash, bank transfer, etc.
    receipt_number = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Income {self.id} - {self.category} - Amount {self.amount}>'
    
    @classmethod
    def create(cls, category, amount, description=None, payment_method='cash', created_by=None):
        """Create a new income"""
        income = cls(
            category=category,
            amount=amount,
            description=description,
            payment_method=payment_method,
            created_by=created_by
        )
        db.session.add(income)
        db.session.commit()
        return income
    
    def approve(self, approved_by):
        """Approve the income"""
        if self.status == 'pending':
            self.status = 'approved'
            self.approved_by = approved_by
            self.approved_at = datetime.utcnow()
            db.session.commit()
    
    def reject(self):
        """Reject the income"""
        if self.status == 'pending':
            self.status = 'rejected'
            db.session.commit()
    
    @classmethod
    def get_by_category(cls, category):
        """Get all incomes for a category"""
        return cls.query.filter_by(category=category).order_by(cls.income_date.desc()).all()
    
    @classmethod
    def get_pending(cls):
        """Get all pending incomes"""
        return cls.query.filter_by(status='pending').order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_approved(cls):
        """Get all approved incomes"""
        return cls.query.filter_by(status='approved').order_by(cls.income_date.desc()).all()
    
    @classmethod
    def get_total_by_category(cls, category, start_date=None, end_date=None):
        """Get total incomes for a category within a date range"""
        query = cls.query.filter_by(category=category, status='approved')
        if start_date:
            query = query.filter(cls.income_date >= start_date)
        if end_date:
            query = query.filter(cls.income_date <= end_date)
        return query.with_entities(db.func.sum(cls.amount)).scalar() or 0 