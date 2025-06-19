from app import db
from datetime import datetime

class IncomeSource(db.Model):
    __tablename__ = 'income_sources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    def __repr__(self):
        return f'<IncomeSource {self.name}>'

class Income(db.Model):
    __tablename__ = 'incomes'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    operation = db.Column(db.String(128), nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)  # cash, check, bank transfer
    income_date = db.Column(db.Date, default=datetime.now().date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    income_source_id = db.Column(db.Integer, db.ForeignKey('income_sources.id'), nullable=False)
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    income_source = db.relationship('IncomeSource', backref='incomes')
    responsible = db.relationship('User', foreign_keys=[responsible_id], backref='incomes')
    def __repr__(self):
        return f'<Income {self.id} - {self.amount}>'

class ExpenseType(db.Model):
    __tablename__ = 'expense_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    def __repr__(self):
        return f'<ExpenseType {self.name}>'

class Expense(db.Model):
    __tablename__ = 'expenses'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    operation = db.Column(db.String(128), nullable=False)
    invoice_number = db.Column(db.String(64), nullable=True)
    expense_date = db.Column(db.Date, default=datetime.now().date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expense_type_id = db.Column(db.Integer, db.ForeignKey('expense_types.id'), nullable=False)
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expense_type = db.relationship('ExpenseType', backref='expenses')
    responsible = db.relationship('User', foreign_keys=[responsible_id], backref='expenses')
    def __repr__(self):
        return f'<Expense {self.id} - {self.amount}>'

class CashBox(db.Model):
    __tablename__ = 'cash_boxes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0)
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    responsible = db.relationship('User', backref='cash_boxes')
    dummy = db.Column(db.Boolean, default=False)  # Temporary field
    
    def __repr__(self):
        return f'<CashBox {self.name}>'

class BankAccount(db.Model):
    __tablename__ = 'bank_accounts'
    id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String(64), nullable=False)
    account_number = db.Column(db.String(64), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0)
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    responsible = db.relationship('User', backref='bank_accounts')
    def __repr__(self):
        return f'<BankAccount {self.bank_name} - {self.account_number}>'

class Transfer(db.Model):
    __tablename__ = 'transfers'
    id = db.Column(db.Integer, primary_key=True)
    from_account = db.Column(db.String(128), nullable=False)  # Format: "cash_box_1" or "bank_account_1"
    to_account = db.Column(db.String(128), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transfer_date = db.Column(db.Date, default=datetime.now().date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    responsible = db.relationship('User', backref='transfers')

    @property
    def from_type(self):
        return 'cash_box' if self.from_account.startswith('cash_box_') else 'bank_account'

    @property
    def to_type(self):
        return 'cash_box' if self.to_account.startswith('cash_box_') else 'bank_account'

    @property
    def from_cash_box(self):
        if self.from_type == 'cash_box':
            cash_box_id = int(self.from_account.split('_')[2])
            from app.models.finance import CashBox
            return CashBox.query.get(cash_box_id)
        return None

    @property
    def to_cash_box(self):
        if self.to_type == 'cash_box':
            cash_box_id = int(self.to_account.split('_')[2])
            from app.models.finance import CashBox
            return CashBox.query.get(cash_box_id)
        return None

    @property
    def from_bank_account(self):
        if self.from_type == 'bank_account':
            bank_account_id = int(self.from_account.split('_')[2])
            from app.models.finance import BankAccount
            return BankAccount.query.get(bank_account_id)
        return None

    @property
    def to_bank_account(self):
        if self.to_type == 'bank_account':
            bank_account_id = int(self.to_account.split('_')[2])
            from app.models.finance import BankAccount
            return BankAccount.query.get(bank_account_id)
        return None

    def __repr__(self):
        return f'<Transfer {self.id} - {self.amount}>'

class Account(db.Model):
    __tablename__ = 'accounts'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    account_type = db.Column(db.String(20), nullable=False)  # cash, bank
    balance = db.Column(db.Float, nullable=False, default=0)
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    responsible = db.relationship('User', backref='accounts')

    def __repr__(self):
        return f'<Account {self.name}>'

class Revenue(db.Model):
    __tablename__ = 'revenues'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    revenue_type = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    revenue_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    account = db.relationship('Account', backref='revenues')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_revenues')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_revenues')

    def __repr__(self):
        return f'<Revenue {self.id} - {self.amount}>'

class Budget(db.Model):
    __tablename__ = 'budgets'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    budget_type = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    account = db.relationship('Account', backref='budgets')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_budgets')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_budgets')

    def __repr__(self):
        return f'<Budget {self.id} - {self.amount}>'

class CashFlow(db.Model):
    __tablename__ = 'cash_flows'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    flow_type = db.Column(db.String(20), nullable=False)  # income, expense, transfer
    amount = db.Column(db.Float, nullable=False)
    flow_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    reference_id = db.Column(db.Integer, nullable=True)  # ID of related model (Revenue, Expense, etc.)
    reference_type = db.Column(db.String(20), nullable=True)  # revenue, expense, transfer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    account = db.relationship('Account', backref='cash_flows')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_cash_flows')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_cash_flows')

    def __repr__(self):
        return f'<CashFlow {self.id} - {self.amount}>'

class ProfitLoss(db.Model):
    __tablename__ = 'profit_loss'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    total_revenue = db.Column(db.Float, nullable=False, default=0)
    total_expense = db.Column(db.Float, nullable=False, default=0)
    net_profit = db.Column(db.Float, nullable=False, default=0)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    account = db.relationship('Account', backref='profit_loss')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_profit_loss')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_profit_loss')

    def __repr__(self):
        return f'<ProfitLoss {self.id} - {self.net_profit}>'
