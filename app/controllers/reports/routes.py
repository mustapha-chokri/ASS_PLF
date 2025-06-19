from flask import render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app.models.report import Report
from app.models.finance import Revenue, Expense, Account
from app.controllers.reports.forms import FinancialReportForm, LiteraryReportForm
from app import db
import pandas as pd
import io
from datetime import datetime
from app.controllers.reports import reports_bp
from sqlalchemy import func
import traceback

@reports_bp.route('/')
@login_required
def index():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('reports/index.html', title='التقارير', reports=reports)

@reports_bp.route('/financial', methods=['GET', 'POST'])
@login_required
def financial():
    form = FinancialReportForm()
    if form.validate_on_submit():
        try:
            # إنشاء تقرير جديد
            report = Report(
                title=f"تقرير {form.report_type.data} - {form.account_type.data} - {form.start_date.data} إلى {form.end_date.data}",
                report_type='financial',
                created_by=current_user.id
            )
            db.session.add(report)
            db.session.commit()
            
            # إنشاء التقرير وتحميله
            return redirect(url_for('reports.download_report', report_id=report.id))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إنشاء التقرير: {str(e)}', 'error')
            return redirect(url_for('reports.financial'))
    
    reports = Report.query.filter_by(report_type='financial').order_by(Report.created_at.desc()).all()
    return render_template('reports/financial.html', title='التقارير المالية', form=form, reports=reports)

@reports_bp.route('/literary', methods=['GET', 'POST'])
@login_required
def literary():
    form = LiteraryReportForm()
    if form.validate_on_submit():
        try:
            # إنشاء تقرير جديد
            report = Report(
                title=f"تقرير {form.report_type.data} - {form.department.data} - {form.start_date.data} إلى {form.end_date.data}",
                report_type='literary',
                created_by=current_user.id
            )
            db.session.add(report)
            db.session.commit()
            
            # إنشاء التقرير وتحميله
            return redirect(url_for('reports.download_report', report_id=report.id))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إنشاء التقرير: {str(e)}', 'error')
            return redirect(url_for('reports.literary'))
    
    reports = Report.query.filter_by(report_type='literary').order_by(Report.created_at.desc()).all()
    return render_template('reports/literary.html', title='التقارير الأدبية', form=form, reports=reports)

@reports_bp.route('/download/<int:report_id>')
@login_required
def download_report(report_id):
    report = Report.query.get_or_404(report_id)
    
    try:
        # تحديث حالة التقرير إلى قيد المعالجة
        report.update_status('processing')
        
        # استخراج معلومات التقرير من العنوان
        title_parts = report.title.split(' - ')
        if len(title_parts) < 3:
            raise ValueError('تنسيق عنوان التقرير غير صحيح')
            
        report_type = title_parts[0].replace('تقرير ', '')
        category = title_parts[1]
        date_range = title_parts[2]
        
        # استخراج التواريخ من النطاق
        try:
            start_date = datetime.strptime(date_range.split(' إلى ')[0], '%Y-%m-%d')
            end_date = datetime.strptime(date_range.split(' إلى ')[1], '%Y-%m-%d')
        except (ValueError, IndexError):
            raise ValueError('تنسيق التاريخ غير صحيح')
        
        # إنشاء DataFrame للتقرير
        if report.report_type == 'financial':
            if report_type == 'revenue' or 'المداخيل' in report_type:
                # إنشاء تقرير الإيرادات
                query = Revenue.query.filter(
                    Revenue.revenue_date.between(start_date.date(), end_date.date()),
                    Revenue.status == 'approved'  # فقط الإيرادات المعتمدة
                )
                
                if category != 'all' and category != 'جميع الحسابات':
                    query = query.join(Account).filter(Account.account_type == category)
                
                revenues = query.all()
                
                if not revenues:
                    report.update_status('failed')
                    flash('لا توجد بيانات للإيرادات في الفترة المحددة. تأكد من وجود إيرادات معتمدة في الفترة المحددة.', 'warning')
                    return redirect(url_for('reports.financial'))
                
                data = {
                    'التاريخ': [revenue.revenue_date.strftime('%Y-%m-%d') for revenue in revenues],
                    'نوع الإيراد': [revenue.revenue_type for revenue in revenues],
                    'المبلغ': [revenue.amount for revenue in revenues],
                    'الحساب': [revenue.account.name if revenue.account else '' for revenue in revenues],
                    'الوصف': [revenue.description for revenue in revenues],
                    'الحالة': [revenue.status for revenue in revenues]
                }
                
            elif report_type == 'expense' or 'المصروفات' in report_type:
                # إنشاء تقرير المصروفات
                query = Expense.query.filter(
                    Expense.expense_date.between(start_date, end_date)
                )
                
                if category != 'all' and category != 'جميع الحسابات':
                    query = query.join(Account).filter(Account.account_type == category)
                
                expenses = query.all()
                
                if not expenses:
                    report.update_status('failed')
                    flash('لا توجد بيانات للمصروفات في الفترة المحددة', 'warning')
                    return redirect(url_for('reports.financial'))
                
                data = {
                    'التاريخ': [expense.expense_date.strftime('%Y-%m-%d') for expense in expenses],
                    'نوع المصروف': [expense.expense_type.name if expense.expense_type else '' for expense in expenses],
                    'المبلغ': [expense.amount for expense in expenses],
                    'الحساب': [expense.account.name if expense.account else '' for expense in expenses],
                    'الوصف': [expense.notes for expense in expenses]
                }
                
            elif report_type == 'budget' or 'الميزانية' in report_type:
                # إنشاء تقرير الميزانية
                total_revenue = db.session.query(func.sum(Revenue.amount)).filter(
                    Revenue.revenue_date.between(start_date, end_date)
                ).scalar() or 0
                
                total_expense = db.session.query(func.sum(Expense.amount)).filter(
                    Expense.expense_date.between(start_date, end_date)
                ).scalar() or 0
                
                if total_revenue == 0 and total_expense == 0:
                    report.update_status('failed')
                    flash('لا توجد بيانات للميزانية في الفترة المحددة', 'warning')
                    return redirect(url_for('reports.financial'))
                
                data = {
                    'البند': ['إجمالي المداخيل', 'إجمالي المصروفات', 'الرصيد'],
                    'المبلغ': [total_revenue, total_expense, total_revenue - total_expense]
                }
                
            elif report_type == 'cash_flow' or 'التدفق النقدي' in report_type:
                # إنشاء تقرير التدفق النقدي
                accounts = Account.query.all()
                cash_flow = []
                
                for account in accounts:
                    if category != 'all' and category != 'جميع الحسابات' and account.account_type != category:
                        continue
                        
                    revenue = db.session.query(func.sum(Revenue.amount)).filter(
                        Revenue.account_id == account.id,
                        Revenue.revenue_date.between(start_date, end_date)
                    ).scalar() or 0
                    
                    expense = db.session.query(func.sum(Expense.amount)).filter(
                        Expense.account_id == account.id,
                        Expense.expense_date.between(start_date, end_date)
                    ).scalar() or 0
                    
                    if revenue > 0 or expense > 0:
                        cash_flow.append({
                            'الحساب': account.name,
                            'نوع الحساب': account.account_type,
                            'المداخيل': revenue,
                            'المصروفات': expense,
                            'الرصيد': revenue - expense
                        })
                
                if not cash_flow:
                    report.update_status('failed')
                    flash('لا توجد بيانات للتدفق النقدي في الفترة المحددة', 'warning')
                    return redirect(url_for('reports.financial'))
                
                data = {
                    'الحساب': [item['الحساب'] for item in cash_flow],
                    'نوع الحساب': [item['نوع الحساب'] for item in cash_flow],
                    'المداخيل': [item['المداخيل'] for item in cash_flow],
                    'المصروفات': [item['المصروفات'] for item in cash_flow],
                    'الرصيد': [item['الرصيد'] for item in cash_flow]
                }
                
            elif report_type == 'profit_loss' or 'الأرباح والخسائر' in report_type:
                # إنشاء تقرير الأرباح والخسائر
                total_revenue = db.session.query(func.sum(Revenue.amount)).filter(
                    Revenue.revenue_date.between(start_date, end_date)
                ).scalar() or 0
                
                total_expense = db.session.query(func.sum(Expense.amount)).filter(
                    Expense.expense_date.between(start_date, end_date)
                ).scalar() or 0
                
                if total_revenue == 0 and total_expense == 0:
                    report.update_status('failed')
                    flash('لا توجد بيانات للأرباح والخسائر في الفترة المحددة', 'warning')
                    return redirect(url_for('reports.financial'))
                
                data = {
                    'البند': ['إجمالي المداخيل', 'إجمالي المصروفات', 'صافي الربح/الخسارة'],
                    'المبلغ': [total_revenue, total_expense, total_revenue - total_expense]
                }
                
            else:
                report.update_status('failed')
                flash(f'نوع التقرير غير معروف: {report_type}', 'error')
                return redirect(url_for('reports.financial'))
        else:
            # تقارير أدبية
            data = {
                'التاريخ': ['2024-01-01', '2024-01-15', '2024-02-01'],
                'النشاط': ['دورة تدريبية', 'محاضرة', 'ورشة عمل'],
                'عدد المشاركين': [20, 50, 30]
            }
        
        df = pd.DataFrame(data)
        
        # إنشاء ملف Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='التقرير', index=False)
        
        output.seek(0)
        
        # تحديث حالة التقرير إلى مكتمل
        report.update_status('completed')
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"{report.title}.xlsx"
        )
    except Exception as e:
        # تحديث حالة التقرير في حالة حدوث خطأ
        report.update_status('failed')
        error_msg = f'حدث خطأ أثناء إنشاء التقرير: {str(e)}\n{traceback.format_exc()}'
        flash(error_msg, 'error')
        return redirect(url_for('reports.index')) 