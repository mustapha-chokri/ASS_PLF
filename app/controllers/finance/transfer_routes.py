from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.controllers.finance import finance_bp
from app.models.finance import Transfer, CashBox, BankAccount
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@finance_bp.route('/add_transfer', methods=['POST'])
@login_required
def add_transfer():
    try:
        # التحقق من وجود جميع الحقول المطلوبة
        required_fields = ['from_account', 'to_account', 'amount', 'transfer_date']
        for field in required_fields:
            if not request.form.get(field):
                flash(f'حقل {field} مطلوب', 'danger')
                return redirect(url_for('finance.treasury'))

        from_account = request.form.get('from_account')
        to_account = request.form.get('to_account')
        amount = float(request.form.get('amount'))
        transfer_date = datetime.strptime(request.form.get('transfer_date'), '%Y-%m-%d').date()
        notes = request.form.get('notes')

        # التحقق من صحة المبلغ
        if amount <= 0:
            flash('يجب أن يكون المبلغ أكبر من صفر', 'danger')
            return redirect(url_for('finance.treasury'))

        # التحقق من عدم التحويل لنفس الحساب
        if from_account == to_account:
            flash('لا يمكن التحويل بين نفس الحساب', 'danger')
            return redirect(url_for('finance.treasury'))

        # التحقق من الرصيد الكافي
        if from_account.startswith('cash_box_'):
            cash_box_id = int(from_account.split('_')[2])
            cash_box = CashBox.query.get(cash_box_id)
            if not cash_box:
                flash('الصندوق المصدر غير موجود', 'danger')
                return redirect(url_for('finance.treasury'))
            if cash_box.balance < amount:
                flash('الرصيد غير كافي في الصندوق المصدر', 'danger')
                return redirect(url_for('finance.treasury'))
        elif from_account.startswith('bank_account_'):
            bank_account_id = int(from_account.split('_')[2])
            bank_account = BankAccount.query.get(bank_account_id)
            if not bank_account:
                flash('الحساب البنكي المصدر غير موجود', 'danger')
                return redirect(url_for('finance.treasury'))
            if bank_account.balance < amount:
                flash('الرصيد غير كافي في الحساب البنكي المصدر', 'danger')
                return redirect(url_for('finance.treasury'))
        else:
            flash('نوع الحساب المصدر غير صحيح', 'danger')
            return redirect(url_for('finance.treasury'))

        # التحقق من وجود الحساب المستلم
        if to_account.startswith('cash_box_'):
            cash_box_id = int(to_account.split('_')[2])
            cash_box = CashBox.query.get(cash_box_id)
            if not cash_box:
                flash('الصندوق المستلم غير موجود', 'danger')
                return redirect(url_for('finance.treasury'))
        elif to_account.startswith('bank_account_'):
            bank_account_id = int(to_account.split('_')[2])
            bank_account = BankAccount.query.get(bank_account_id)
            if not bank_account:
                flash('الحساب البنكي المستلم غير موجود', 'danger')
                return redirect(url_for('finance.treasury'))
        else:
            flash('نوع الحساب المستلم غير صحيح', 'danger')
            return redirect(url_for('finance.treasury'))

        # إنشاء التحويل
        transfer = Transfer(
            from_account=from_account,
            to_account=to_account,
            amount=amount,
            transfer_date=transfer_date,
            notes=notes,
            responsible_id=current_user.id
        )
        db.session.add(transfer)

        # تحديث الأرصدة
        if from_account.startswith('cash_box_'):
            cash_box_id = int(from_account.split('_')[2])
            cash_box = CashBox.query.get(cash_box_id)
            cash_box.balance -= amount
        elif from_account.startswith('bank_account_'):
            bank_account_id = int(from_account.split('_')[2])
            bank_account = BankAccount.query.get(bank_account_id)
            bank_account.balance -= amount

        if to_account.startswith('cash_box_'):
            cash_box_id = int(to_account.split('_')[2])
            cash_box = CashBox.query.get(cash_box_id)
            cash_box.balance += amount
        elif to_account.startswith('bank_account_'):
            bank_account_id = int(to_account.split('_')[2])
            bank_account = BankAccount.query.get(bank_account_id)
            bank_account.balance += amount

        db.session.commit()
        flash('تم إضافة التحويل بنجاح', 'success')
        logger.info(f'تم إضافة تحويل جديد: من {from_account} إلى {to_account} بمبلغ {amount}')
    except ValueError as e:
        db.session.rollback()
        flash('قيمة غير صحيحة في أحد الحقول', 'danger')
        logger.error(f'خطأ في قيمة الحقول: {str(e)}')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء إضافة التحويل: {str(e)}', 'danger')
        logger.error(f'خطأ في إضافة التحويل: {str(e)}')

    return redirect(url_for('finance.treasury')) 