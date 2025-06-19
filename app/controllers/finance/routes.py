from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, jsonify
from flask_login import login_required, current_user
from app import db
from app.controllers.finance import finance_bp
from app.models.finance import Income, Expense, CashBox, BankAccount, ExpenseType, IncomeSource, Transfer
from app.models.user import User
import pandas as pd
import io
from datetime import datetime, date
from types import SimpleNamespace
from sqlalchemy import func, desc, literal
import os
from app.forms.finance import AddIncomeForm

@finance_bp.route('/')
@login_required
def index():
    treasury_balance = db.session.query(db.func.sum(Income.amount) - db.func.sum(Expense.amount)).scalar() or 0
    current_year = datetime.now().year
    yearly_income = db.session.query(db.func.sum(Income.amount))\
        .filter(db.extract('year', Income.income_date) == current_year)\
        .scalar() or 0
    yearly_expense = db.session.query(db.func.sum(Expense.amount))\
        .filter(db.extract('year', Expense.expense_date) == current_year)\
        .scalar() or 0
    recent_income = Income.query.order_by(Income.income_date.desc()).limit(5).all()
    recent_expense = Expense.query.order_by(Expense.expense_date.desc()).limit(5).all()
    monthly_income = [0] * 12
    monthly_expense = [0] * 12
    for month in range(1, 13):
        month_income = db.session.query(db.func.sum(Income.amount))\
            .filter(db.extract('year', Income.income_date) == current_year)\
            .filter(db.extract('month', Income.income_date) == month)\
            .scalar() or 0
        monthly_income[month-1] = float(month_income)
        month_expense = db.session.query(db.func.sum(Expense.amount))\
            .filter(db.extract('year', Expense.expense_date) == current_year)\
            .filter(db.extract('month', Expense.expense_date) == month)\
            .scalar() or 0
        monthly_expense[month-1] = float(month_expense)
    return render_template('finance/index.html',
        title='المالية',
        treasury_balance=treasury_balance,
        yearly_income=yearly_income,
        yearly_expense=yearly_expense,
        recent_income=recent_income,
        recent_expense=recent_expense,
        monthly_income=monthly_income,
        monthly_expense=monthly_expense)

@finance_bp.route('/treasury')
@login_required
def treasury():
    # حساب الرصيد من المصاريف والمدخولات
    total_income = db.session.query(func.sum(Income.amount)).scalar() or 0
    total_expense = db.session.query(func.sum(Expense.amount)).scalar() or 0

    # حساب مجموع أرصدة الحسابات البنكية
    total_bank_balance = db.session.query(func.sum(BankAccount.balance)).scalar() or 0

    # حساب مجموع أرصدة الصناديق النقدية
    total_cash_balance = db.session.query(func.sum(CashBox.balance)).scalar() or 0

    # حساب الرصيد الكلي للخزينة
    current_balance = total_income - total_expense + total_bank_balance + total_cash_balance

    # إنشاء كائن treasury بسيط
    treasury = SimpleNamespace(
        balance=current_balance,
        last_updated=datetime.utcnow()
    )

    # جلب آخر العمليات
    recent_operations = db.session.query(
        Income.id.label('id'),
        Income.operation.label('operation'),
        Income.amount.label('amount'),
        Income.income_date.label('date'),
        literal('income').label('type')
    ).union(
        db.session.query(
            Expense.id.label('id'),
            Expense.operation.label('operation'),
            Expense.amount.label('amount'),
            Expense.expense_date.label('date'),
            literal('expense').label('type')
        )
    ).order_by(desc('date')).limit(10).all()

    # جلب التحويلات
    transfers = Transfer.query.order_by(Transfer.transfer_date.desc()).all()

    # جلب الصناديق والحسابات البنكية
    cash_boxes = CashBox.query.all()
    bank_accounts = BankAccount.query.all()

    return render_template('finance/treasury.html',
                          treasury=treasury,
                          recent_operations=recent_operations,
                          total_income=total_income,
                          total_expense=total_expense,
                          total_bank_balance=total_bank_balance,
                          total_cash_balance=total_cash_balance,
                          transfers=transfers,
                          cash_boxes=cash_boxes,
                          bank_accounts=bank_accounts)

@finance_bp.route('/income')
@login_required
def income():
    # الحصول على معايير التصفية
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    source_id = request.args.get('source_id')
    payment_type = request.args.get('payment_type')
    
    # بناء الاستعلام
    query = Income.query
    
    if start_date:
        query = query.filter(Income.income_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Income.income_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    if source_id:
        query = query.filter(Income.income_source_id == int(source_id))
    if payment_type:
        query = query.filter(Income.payment_type == payment_type)
    
    # الحصول على النتائج
    incomes = query.order_by(Income.income_date.desc()).all()
    
    # حساب المجموع
    total_amount = sum(income.amount for income in incomes)
    
    # الحصول على قوائم التصفية
    income_sources = IncomeSource.query.all()
    payment_types = db.session.query(Income.payment_type).distinct().all()
    payment_types = [pt[0] for pt in payment_types]
    
    # إحصائيات للرسم البياني
    source_stats = db.session.query(
        IncomeSource.name,
        db.func.sum(Income.amount).label('total')
    ).join(Income).group_by(IncomeSource.name).order_by(db.desc('total')).limit(5).all()
    
    # تحضير بيانات الرسم البياني
    chart_labels = [stat[0] for stat in source_stats]
    chart_data = [float(stat[1]) for stat in source_stats]
    
    users = User.query.all()  # إضافة قائمة المستخدمين
    form = AddIncomeForm()
    return render_template('finance/income.html', 
                         title='المداخيل',
                         incomes=incomes,
                         income_sources=income_sources,
                         payment_types=payment_types,
                         users=users,
                         total_amount=total_amount,
                         chart_labels=chart_labels,
                         chart_data=chart_data,
                         today=date.today().strftime('%Y-%m-%d'),
                         form=form)

@finance_bp.route('/export_incomes')
@login_required
def export_incomes():
    incomes = Income.query.order_by(Income.income_date.desc()).all()
    data = []
    for income in incomes:
        data.append({
            'العملية': income.operation,
            'المبلغ': income.amount,
            'التاريخ': income.income_date.strftime('%Y-%m-%d'),
            'نوع الدفع': income.payment_type,
            'المصدر': income.income_source.name if income.income_source else '',
            'المسؤول': income.responsible.full_name if income.responsible else '',
            'ملاحظات': income.notes or ''
        })
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='المداخيل', index=False)
        workbook = writer.book
        worksheet = writer.sheets['المداخيل']
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'align': 'center',
            'bg_color': '#D9E1F2',
            'border': 1
        })
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'incomes_{date.today().strftime("%Y%m%d")}.xlsx'
    )

@finance_bp.route('/import_incomes', methods=['POST'])
@login_required
def import_incomes():
    if 'file' not in request.files:
        flash('لم يتم اختيار ملف', 'danger')
        return redirect(url_for('finance.income'))
    
    file = request.files['file']
    if file.filename == '':
        flash('لم يتم اختيار ملف', 'danger')
        return redirect(url_for('finance.income'))
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        flash('يجب أن يكون الملف بصيغة Excel', 'danger')
        return redirect(url_for('finance.income'))
    
    try:
        df = pd.read_excel(file)
        required_columns = ['العملية', 'المبلغ', 'التاريخ', 'نوع الدفع', 'المصدر', 'المسؤول']
        if not all(col in df.columns for col in required_columns):
            flash('الملف لا يحتوي على جميع الأعمدة المطلوبة', 'danger')
            return redirect(url_for('finance.income'))
        
        for _, row in df.iterrows():
            # البحث عن مصدر المدخول
            income_source = IncomeSource.query.filter_by(name=row['المصدر']).first()
            if not income_source:
                income_source = IncomeSource(name=row['المصدر'])
                db.session.add(income_source)
                db.session.commit()
            
            # البحث عن المسؤول
            responsible = User.query.filter_by(full_name=row['المسؤول']).first()
            if not responsible:
                flash(f'المستخدم {row["المسؤول"]} غير موجود', 'danger')
                continue
            
            # إنشاء مدخول جديد
            income = Income(
                operation=row['العملية'],
                amount=float(row['المبلغ']),
                income_date=pd.to_datetime(row['التاريخ']).date(),
                payment_type=row['نوع الدفع'],
                income_source_id=income_source.id,
                responsible_id=responsible.id,
                notes=row.get('ملاحظات', ''),
                created_by=current_user.id
            )
            db.session.add(income)
        
        db.session.commit()
        flash('تم استيراد المداخيل بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء استيراد الملف: {str(e)}', 'danger')
    
    return redirect(url_for('finance.income'))

@finance_bp.route('/download_income_template')
@login_required
def download_income_template():
    # استخدام المسار المطلق من مجلد المشروع
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    template_path = os.path.join(base_dir, 'app', 'static', 'templates', 'income_template.xlsx')
    if not os.path.exists(template_path):
        from create_income_template import create_income_template
        create_income_template()
    return send_file(
        template_path,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='income_template.xlsx'
    )

@finance_bp.route('/download_expense_template')
@login_required
def download_expense_template():
    # استخدام المسار النسبي من جذر المشروع
    template_path = os.path.join('app', 'static', 'templates', 'expense_template.xlsx')

    # بناء المسار الكامل باستخدام مسار العمل الحالي
    full_template_path = os.path.join(os.getcwd(), template_path)

    if not os.path.exists(full_template_path):
        # استيراد وإنشاء القالب إذا لم يكن موجوداً
        try:
            from create_expense_template import create_expense_template
            create_expense_template()
        except ImportError:
            flash('خطأ: ملف إنشاء قالب المصاريف غير موجود.', 'danger')
            return redirect(url_for('finance.expense'))
        except Exception as e:
            flash(f'خطأ أثناء إنشاء قالب المصاريف: {str(e)}', 'danger')
            return redirect(url_for('finance.expense'))

    return send_file(
        full_template_path,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='expense_template.xlsx'
    )

@finance_bp.route('/expense')
@login_required
def expense():
    # الحصول على معايير التصفية
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    type_id = request.args.get('type_id')
    
    # بناء الاستعلام
    query = Expense.query
    
    if start_date:
        query = query.filter(Expense.expense_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Expense.expense_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    if type_id:
        query = query.filter(Expense.expense_type_id == int(type_id))
    
    # الحصول على النتائج
    expenses = query.order_by(Expense.expense_date.desc()).all()
    
    # حساب المجموع
    total_amount = sum(expense.amount for expense in expenses)
    
    # الحصول على قوائم التصفية
    expense_types = ExpenseType.query.all()
    
    # إحصائيات للرسم البياني
    type_stats = db.session.query(
        ExpenseType.name,
        db.func.sum(Expense.amount).label('total')
    ).join(Expense).group_by(ExpenseType.name).order_by(db.desc('total')).limit(5).all()
    
    # تحضير بيانات الرسم البياني
    chart_labels = [stat[0] for stat in type_stats]
    chart_data = [float(stat[1]) for stat in type_stats]
    
    users = User.query.all()  # إضافة قائمة المستخدمين
    return render_template('finance/expense.html', 
                         title='المصاريف',
                         expenses=expenses,
                         expense_types=expense_types,
                         users=users,  # إضافة قائمة المستخدمين
                         total_amount=total_amount,
                         chart_labels=chart_labels,
                         chart_data=chart_data,
                         today=date.today().strftime('%Y-%m-%d'))

@finance_bp.route('/export_expenses')
@login_required
def export_expenses():
    expenses = Expense.query.order_by(Expense.expense_date.desc()).all()
    data = []
    for expense in expenses:
        data.append({
            'العملية': expense.operation,
            'المبلغ': expense.amount,
            'التاريخ': expense.expense_date.strftime('%Y-%m-%d'),
            'نوع المصروف': expense.expense_type.name if expense.expense_type else '',
            'المسؤول': expense.responsible.full_name if expense.responsible else '',
            'رقم الفاتورة': expense.invoice_number or '',
            'ملاحظات': expense.notes or ''
        })
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='المصاريف', index=False)
        workbook = writer.book
        worksheet = writer.sheets['المصاريف']
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'align': 'center',
            'bg_color': '#D9E1F2',
            'border': 1
        })
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'expenses_{date.today().strftime("%Y%m%d")}.xlsx'
    )

@finance_bp.route('/import_expenses', methods=['POST'])
@login_required
def import_expenses():
    if 'file' not in request.files:
        flash('لم يتم اختيار ملف', 'danger')
        return redirect(url_for('finance.expense'))
    
    file = request.files['file']
    if file.filename == '':
        flash('لم يتم اختيار ملف', 'danger')
        return redirect(url_for('finance.expense'))
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        flash('يجب أن يكون الملف بصيغة Excel', 'danger')
        return redirect(url_for('finance.expense'))
    
    try:
        df = pd.read_excel(file)
        required_columns = ['العملية', 'المبلغ', 'التاريخ', 'نوع المصروف', 'المسؤول']
        if not all(col in df.columns for col in required_columns):
            flash('الملف لا يحتوي على جميع الأعمدة المطلوبة', 'danger')
            return redirect(url_for('finance.expense'))
        
        for _, row in df.iterrows():
            # البحث عن نوع المصروف
            expense_type = ExpenseType.query.filter_by(name=row['نوع المصروف']).first()
            if not expense_type:
                expense_type = ExpenseType(name=row['نوع المصروف'])
                db.session.add(expense_type)
                db.session.commit()
            
            # البحث عن المسؤول
            responsible = User.query.filter_by(full_name=row['المسؤول']).first()
            if not responsible:
                flash(f'المستخدم {row["المسؤول"]} غير موجود', 'danger')
                continue
            
            # إنشاء مصروف جديد
            expense = Expense(
                operation=row['العملية'],
                amount=float(row['المبلغ']),
                expense_date=pd.to_datetime(row['التاريخ']).date(),
                expense_type_id=expense_type.id,
                responsible_id=responsible.id,
                invoice_number=row.get('رقم الفاتورة', ''),
                notes=row.get('ملاحظات', ''),
                created_by=current_user.id
            )
            db.session.add(expense)
        
        db.session.commit()
        flash('تم استيراد المصاريف بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء استيراد الملف: {str(e)}', 'danger')
    
    return redirect(url_for('finance.expense'))

@finance_bp.route('/expense_types')
@login_required
def expense_types():
    expense_types = ExpenseType.query.all()
    return render_template('finance/expense_types.html',
                         title='أنواع المصاريف',
                         expense_types=expense_types)

@finance_bp.route('/income_sources')
@login_required
def income_sources():
    income_sources = IncomeSource.query.all()
    return render_template('finance/income_sources.html',
                         title='مصادر المداخيل',
                         income_sources=income_sources)

@finance_bp.route('/add_income', methods=['POST'])
@login_required
def add_income():
    operation = request.form.get('operation')
    amount = request.form.get('amount')
    income_date = request.form.get('income_date')
    payment_type = request.form.get('payment_type')
    income_source_id = request.form.get('income_source_id')
    responsible_id = request.form.get('responsible_id')
    notes = request.form.get('notes')
    if not (operation and amount and income_date and payment_type and income_source_id and responsible_id):
        flash('جميع الحقول المطلوبة يجب ملؤها', 'danger')
        return redirect(url_for('finance.income'))
    income = Income(
        operation=operation,
        amount=float(amount),
        income_date=datetime.strptime(income_date, '%Y-%m-%d').date(),
        payment_type=payment_type,
        income_source_id=int(income_source_id),
        responsible_id=int(responsible_id),
        notes=notes,
        created_by=current_user.id
    )
    db.session.add(income)
    db.session.commit()
    flash('تمت إضافة المدخول بنجاح', 'success')
    return redirect(url_for('finance.income'))

@finance_bp.route('/add_income_source', methods=['POST'])
@login_required
def add_income_source():
    name = request.form.get('name')
    if not name:
        flash('يجب إدخال اسم مصدر المدخول', 'danger')
        return redirect(url_for('finance.income_sources'))
    
    # التحقق من عدم وجود مصدر مدخول بنفس الاسم
    existing_source = IncomeSource.query.filter_by(name=name).first()
    if existing_source:
        flash('يوجد مصدر مدخول بنفس الاسم', 'danger')
        return redirect(url_for('finance.income_sources'))
    
    income_source = IncomeSource(name=name)
    db.session.add(income_source)
    db.session.commit()
    flash('تم إضافة مصدر المدخول بنجاح', 'success')
    return redirect(url_for('finance.income_sources'))

@finance_bp.route('/delete_income_source/<int:id>', methods=['POST'])
@login_required
def delete_income_source(id):
    income_source = IncomeSource.query.get_or_404(id)
    try:
        # التحقق من عدم وجود مداخيل مرتبطة بهذا المصدر
        if income_source.incomes:
            flash('لا يمكن حذف مصدر المدخول لوجود مداخيل مرتبطة به', 'danger')
            return redirect(url_for('finance.income_sources'))
        
        db.session.delete(income_source)
        db.session.commit()
        flash('تم حذف مصدر المدخول بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ أثناء حذف مصدر المدخول', 'danger')
    return redirect(url_for('finance.income_sources'))

@finance_bp.route('/edit_income_source/<int:id>', methods=['POST'])
@login_required
def edit_income_source(id):
    income_source = IncomeSource.query.get_or_404(id)
    name = request.form.get('name')
    
    if not name:
        flash('يجب إدخال اسم مصدر المدخول', 'danger')
        return redirect(url_for('finance.income_sources'))
    
    # التحقق من عدم وجود مصدر مدخول آخر بنفس الاسم
    existing_source = IncomeSource.query.filter(IncomeSource.name == name, IncomeSource.id != id).first()
    if existing_source:
        flash('يوجد مصدر مدخول آخر بنفس الاسم', 'danger')
        return redirect(url_for('finance.income_sources'))
    
    try:
        income_source.name = name
        db.session.commit()
        flash('تم تعديل مصدر المدخول بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ أثناء تعديل مصدر المدخول', 'danger')
    
    return redirect(url_for('finance.income_sources'))

@finance_bp.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    operation = request.form.get('operation')
    amount = request.form.get('amount')
    expense_date = request.form.get('expense_date')
    expense_type_id = request.form.get('expense_type_id')
    responsible_id = request.form.get('responsible_id')
    invoice_number = request.form.get('invoice_number')
    notes = request.form.get('notes')
    if not (operation and amount and expense_date and expense_type_id and responsible_id):
        flash('جميع الحقول المطلوبة يجب ملؤها', 'danger')
        return redirect(url_for('finance.expense'))
    expense = Expense(
        operation=operation,
        amount=float(amount),
        expense_date=datetime.strptime(expense_date, '%Y-%m-%d').date(),
        expense_type_id=int(expense_type_id),
        responsible_id=int(responsible_id),
        invoice_number=invoice_number,
        notes=notes,
        created_by=current_user.id
    )
    db.session.add(expense)
    db.session.commit()
    flash('تمت إضافة المصروف بنجاح', 'success')
    return redirect(url_for('finance.expense'))

@finance_bp.route('/delete_income/<int:id>', methods=['POST'])
@login_required
def delete_income(id):
    income = Income.query.get_or_404(id)
    try:
        db.session.delete(income)
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم حذف المدخول بنجاح'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء حذف المدخول'}), 500

@finance_bp.route('/delete_expense/<int:id>', methods=['POST'])
@login_required
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    try:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم حذف المصروف بنجاح'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء حذف المصروف'}), 500

@finance_bp.route('/add_expense_type', methods=['POST'])
@login_required
def add_expense_type():
    name = request.form.get('name')
    if not name:
        flash('يجب إدخال اسم نوع المصروف', 'danger')
        return redirect(url_for('finance.expense_types'))
    
    # التحقق من عدم وجود نوع مصروف بنفس الاسم
    existing_type = ExpenseType.query.filter_by(name=name).first()
    if existing_type:
        flash('يوجد نوع مصروف بنفس الاسم', 'danger')
        return redirect(url_for('finance.expense_types'))
    
    expense_type = ExpenseType(name=name)
    db.session.add(expense_type)
    db.session.commit()
    flash('تم إضافة نوع المصروف بنجاح', 'success')
    return redirect(url_for('finance.expense_types'))

@finance_bp.route('/delete_expense_type/<int:id>', methods=['POST'])
@login_required
def delete_expense_type(id):
    expense_type = ExpenseType.query.get_or_404(id)
    try:
        # التحقق من عدم وجود مصاريف مرتبطة بهذا النوع
        if expense_type.expenses:
            flash('لا يمكن حذف نوع المصروف لوجود مصاريف مرتبطة به', 'danger')
            return redirect(url_for('finance.expense_types'))
        
        db.session.delete(expense_type)
        db.session.commit()
        flash('تم حذف نوع المصروف بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ أثناء حذف نوع المصروف', 'danger')
    return redirect(url_for('finance.expense_types'))

@finance_bp.route('/edit_expense_type/<int:id>', methods=['POST'])
@login_required
def edit_expense_type(id):
    expense_type = ExpenseType.query.get_or_404(id)
    name = request.form.get('name')
    
    if not name:
        flash('يجب إدخال اسم نوع المصروف', 'danger')
        return redirect(url_for('finance.expense_types'))
    
    # التحقق من عدم وجود نوع مصروف آخر بنفس الاسم
    existing_type = ExpenseType.query.filter(ExpenseType.name == name, ExpenseType.id != id).first()
    if existing_type:
        flash('يوجد نوع مصروف آخر بنفس الاسم', 'danger')
        return redirect(url_for('finance.expense_types'))
    
    try:
        expense_type.name = name
        db.session.commit()
        flash('تم تعديل نوع المصروف بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ أثناء تعديل نوع المصروف', 'danger')
    
    return redirect(url_for('finance.expense_types'))

@finance_bp.route('/income/<int:id>')
@login_required
def get_income(id):
    income = Income.query.get_or_404(id)
    return jsonify({
        'income': {
            'operation': income.operation,
            'amount': income.amount,
            'income_date': income.income_date.strftime('%Y-%m-%d'),
            'payment_type': income.payment_type,
            'income_source_id': income.income_source_id,
            'responsible_id': income.responsible_id,
            'notes': income.notes
        }
    })

@finance_bp.route('/expense/<int:id>')
@login_required
def get_expense(id):
    expense = Expense.query.get_or_404(id)
    return jsonify({
        'expense': {
            'operation': expense.operation,
            'amount': expense.amount,
            'expense_date': expense.expense_date.strftime('%Y-%m-%d'),
            'expense_type_id': expense.expense_type_id,
            'responsible_id': expense.responsible_id,
            'invoice_number': expense.invoice_number,
            'notes': expense.notes
        }
    })

@finance_bp.route('/edit_income/<int:id>', methods=['POST'])
@login_required
def edit_income(id):
    income = Income.query.get_or_404(id)
    try:
        income.operation = request.form.get('operation')
        income.amount = float(request.form.get('amount'))
        income.income_date = datetime.strptime(request.form.get('income_date'), '%Y-%m-%d').date()
        income.payment_type = request.form.get('payment_type')
        income.income_source_id = int(request.form.get('income_source_id'))
        income.responsible_id = int(request.form.get('responsible_id'))
        income.notes = request.form.get('notes')
        
        db.session.commit()
        flash('تم تعديل المدخول بنجاح', 'success')
        return redirect(url_for('finance.income'))
    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ أثناء تعديل المدخول', 'danger')
        return redirect(url_for('finance.income'))

@finance_bp.route('/edit_expense/<int:id>', methods=['POST'])
@login_required
def edit_expense(id):
    expense = Expense.query.get_or_404(id)
    try:
        expense.operation = request.form.get('operation')
        expense.amount = float(request.form.get('amount'))
        expense.expense_date = datetime.strptime(request.form.get('expense_date'), '%Y-%m-%d').date()
        expense.expense_type_id = int(request.form.get('expense_type_id'))
        expense.responsible_id = int(request.form.get('responsible_id'))
        expense.invoice_number = request.form.get('invoice_number')
        expense.notes = request.form.get('notes')
        
        db.session.commit()
        flash('تم تعديل المصروف بنجاح', 'success')
        return redirect(url_for('finance.expense'))
    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ أثناء تعديل المصروف', 'danger')
        return redirect(url_for('finance.expense'))

@finance_bp.route('/add_account', methods=['GET', 'POST'])
@login_required
def add_account():
    if request.method == 'POST':
        account_type = request.form.get('account_type')
        initial_balance = float(request.form.get('initial_balance', 0))
        notes = request.form.get('notes')
        
        if account_type == 'cash_box':
            name = request.form.get('name')
            if not name:
                flash('يرجى إدخال اسم الصندوق', 'danger')
                return redirect(url_for('finance.add_account'))
            
            cash_box = CashBox(
                name=name,
                balance=initial_balance,
                responsible_id=current_user.id,
                notes=notes
            )
            db.session.add(cash_box)
            
        elif account_type == 'bank_account':
            bank_name = request.form.get('bank_name')
            account_number = request.form.get('account_number')
            
            if not bank_name or not account_number:
                flash('يرجى إدخال اسم البنك ورقم الحساب', 'danger')
                return redirect(url_for('finance.add_account'))
            
            bank_account = BankAccount(
                bank_name=bank_name,
                account_number=account_number,
                balance=initial_balance,
                responsible_id=current_user.id,
                notes=notes
            )
            db.session.add(bank_account)
        
        try:
            db.session.commit()
            flash('تم إضافة الحساب بنجاح', 'success')
            return redirect(url_for('finance.treasury'))
        except Exception as e:
            db.session.rollback()
            flash('حدث خطأ أثناء إضافة الحساب', 'danger')
            return redirect(url_for('finance.add_account'))
    
    return render_template('finance/add_account.html')

@finance_bp.route('/bank_account/<int:id>')
@login_required
def get_bank_account(id):
    account = BankAccount.query.get_or_404(id)
    return jsonify({
        'bank_name': account.bank_name,
        'account_number': account.account_number,
        'balance': account.balance,
        'notes': account.notes
    })

@finance_bp.route('/cash_box/<int:id>')
@login_required
def get_cash_box(id):
    box = CashBox.query.get_or_404(id)
    return jsonify({
        'name': box.name,
        'balance': box.balance,
        'notes': box.notes
    })

@finance_bp.route('/add_bank_account', methods=['POST'])
@login_required
def add_bank_account():
    try:
        bank_name = request.form.get('bank_name')
        account_number = request.form.get('account_number')
        balance = float(request.form.get('balance', 0))
        notes = request.form.get('notes')
        new_account = BankAccount(
            bank_name=bank_name,
            account_number=account_number,
            balance=balance,
            notes=notes,
            responsible_id=current_user.id
        )
        db.session.add(new_account)
        db.session.commit()
        flash('تم إضافة الحساب البنكي بنجاح', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ أثناء إضافة الحساب البنكي', 'error')
        return jsonify({'success': False, 'error': str(e)}), 400

@finance_bp.route('/add_cash_box', methods=['POST'])
@login_required
def add_cash_box():
    try:
        name = request.form.get('name')
        balance = float(request.form.get('balance', 0))
        notes = request.form.get('notes')
        new_box = CashBox(
            name=name,
            balance=balance,
            notes=notes,
            responsible_id=current_user.id
        )
        db.session.add(new_box)
        db.session.commit()
        flash('تم إضافة الصندوق النقدي بنجاح', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ أثناء إضافة الصندوق النقدي', 'error')
        return jsonify({'success': False, 'error': str(e)}), 400

@finance_bp.route('/edit_bank_account/<int:id>', methods=['POST'])
@login_required
def edit_bank_account(id):
    try:
        account = BankAccount.query.get_or_404(id)
        account.bank_name = request.form.get('bank_name')
        account.account_number = request.form.get('account_number')
        account.balance = float(request.form.get('balance', 0))
        account.notes = request.form.get('notes')
        db.session.commit()
        flash('تم تحديث الحساب البنكي بنجاح', 'success')
        return jsonify({'success': True})
    except Exception as e:
        print('BANK EDIT ERROR:', e)  # أضف هذا السطر
        db.session.rollback()
        flash('حدث خطأ أثناء تحديث الحساب البنكي', 'error')
        return jsonify({'success': False, 'error': str(e)}), 400

@finance_bp.route('/edit_cash_box/<int:id>', methods=['POST'])
@login_required
def edit_cash_box(id):
    try:
        box = CashBox.query.get_or_404(id)
        box.name = request.form.get('name')
        box.balance = float(request.form.get('balance', 0))
        box.notes = request.form.get('notes')
        
        db.session.commit()
        flash('تم تحديث الصندوق النقدي بنجاح', 'success')
        return jsonify({'success': True})
    except Exception as e:
        print('CASH BOX EDIT ERROR:', e)  # أضف هذا السطر
        db.session.rollback()
        flash('حدث خطأ أثناء تحديث الصندوق النقدي', 'error')
        return jsonify({'success': False, 'error': str(e)}), 400

@finance_bp.route('/bank_account/<int:id>/delete', methods=['POST'])
@login_required
def delete_bank_account(id):
    try:
        account = BankAccount.query.get_or_404(id)
        db.session.delete(account)
        db.session.commit()
        flash('تم حذف الحساب البنكي بنجاح', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ أثناء حذف الحساب البنكي', 'error')
        return jsonify({'success': False, 'error': str(e)}), 400

@finance_bp.route('/cash_box/<int:id>/delete', methods=['POST'])
@login_required
def delete_cash_box(id):
    try:
        box = CashBox.query.get_or_404(id)
        db.session.delete(box)
        db.session.commit()
        flash('تم حذف الصندوق النقدي بنجاح', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ أثناء حذف الصندوق النقدي', 'error')
        return jsonify({'success': False, 'error': str(e)}), 400

@finance_bp.route('/reports')
@login_required
def reports():
    return render_template('finance/reports.html')

