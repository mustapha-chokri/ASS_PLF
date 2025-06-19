from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from app.models import Income, Expense, ExpenseType, IncomeSource, db
from app.controllers.finance import finance_bp

@finance_bp.route('/')
@login_required
def index():
    # إحصائيات عامة
    treasury_balance = db.session.query(func.sum(Income.amount) - func.sum(Expense.amount)).scalar() or 0
    
    # المداخيل والمصاريف السنوية
    current_year = datetime.now().year
    yearly_income = db.session.query(func.sum(Income.amount))\
        .filter(extract('year', Income.date) == current_year)\
        .scalar() or 0
    
    yearly_expense = db.session.query(func.sum(Expense.amount))\
        .filter(extract('year', Expense.date) == current_year)\
        .scalar() or 0

    # المداخيل والمصاريف الأخيرة
    recent_income = Income.query.order_by(Income.date.desc()).limit(5).all()
    recent_expense = Expense.query.order_by(Expense.date.desc()).limit(5).all()

    # بيانات الرسم البياني الشهري
    monthly_income = [0] * 12
    monthly_expense = [0] * 12

    # نحصل على بيانات كل شهر
    for month in range(1, 13):
        month_income = db.session.query(func.sum(Income.amount))\
            .filter(extract('year', Income.date) == current_year)\
            .filter(extract('month', Income.date) == month)\
            .scalar() or 0
        monthly_income[month-1] = float(month_income)

        month_expense = db.session.query(func.sum(Expense.amount))\
            .filter(extract('year', Expense.date) == current_year)\
            .filter(extract('month', Expense.date) == month)\
            .scalar() or 0
        monthly_expense[month-1] = float(month_expense)

    return render_template('finance/index.html',
                         treasury_balance=treasury_balance,
                         yearly_income=yearly_income,
                         yearly_expense=yearly_expense,
                         recent_income=recent_income,
                         recent_expense=recent_expense,
                         monthly_income=monthly_income,
                         monthly_expense=monthly_expense)

@finance_bp.route('/dashboard')
@login_required
def dashboard():
    # إحصائيات عامة
    total_income = db.session.query(func.sum(Income.amount)).scalar() or 0
    total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or 0
    balance = total_income - total_expenses
    total_transactions = db.session.query(func.count(Income.id)).scalar() or 0
    total_transactions += db.session.query(func.count(Expense.id)).scalar() or 0

    # المداخيل والمصاريف الأخيرة
    recent_incomes = Income.query.order_by(Income.date.desc()).limit(5).all()
    recent_expenses = Expense.query.order_by(Expense.date.desc()).limit(5).all()

    # بيانات الرسم البياني للمداخيل والمصاريف
    # نحصل على آخر 6 أشهر
    today = datetime.now()
    dates = []
    income_data = []
    expense_data = []

    for i in range(5, -1, -1):
        month = today - timedelta(days=30*i)
        dates.append(month.strftime('%Y-%m'))
        
        # مجموع المداخيل للشهر
        month_income = db.session.query(func.sum(Income.amount))\
            .filter(extract('year', Income.date) == month.year)\
            .filter(extract('month', Income.date) == month.month)\
            .scalar() or 0
        income_data.append(float(month_income))
        
        # مجموع المصاريف للشهر
        month_expense = db.session.query(func.sum(Expense.amount))\
            .filter(extract('year', Expense.date) == month.year)\
            .filter(extract('month', Expense.date) == month.month)\
            .scalar() or 0
        expense_data.append(float(month_expense))

    # بيانات الرسم البياني الدائري لأنواع المصاريف
    expense_types = []
    expense_type_data = []
    
    # نحصل على مجموع المصاريف لكل نوع
    type_totals = db.session.query(
        ExpenseType.name,
        func.sum(Expense.amount)
    ).join(Expense).group_by(ExpenseType.name).all()
    
    for type_name, total in type_totals:
        expense_types.append(type_name)
        expense_type_data.append(float(total))

    return render_template('finance/finance_dashboard.html',
                         total_income=total_income,
                         total_expenses=total_expenses,
                         balance=balance,
                         total_transactions=total_transactions,
                         recent_incomes=recent_incomes,
                         recent_expenses=recent_expenses,
                         dates=dates,
                         income_data=income_data,
                         expense_data=expense_data,
                         expense_types=expense_types,
                         expense_type_data=expense_type_data) 