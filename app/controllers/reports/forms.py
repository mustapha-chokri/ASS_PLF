from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional

class FinancialReportForm(FlaskForm):
    report_type = SelectField('نوع التقرير', choices=[
        ('revenue', 'تقرير المداخيل'),
        ('expense', 'تقرير المصروفات'),
        ('budget', 'تقرير الميزانية'),
        ('cash_flow', 'تقرير التدفق النقدي'),
        ('profit_loss', 'تقرير الأرباح والخسائر')
    ], validators=[DataRequired()])
    
    account_type = SelectField('نوع الحساب', choices=[
        ('all', 'جميع الحسابات'),
        ('cash', 'الصندوق النقدي'),
        ('bank', 'الحساب البنكي'),
        ('other', 'حسابات أخرى')
    ], validators=[DataRequired()])
    
    start_date = DateField('تاريخ البداية', validators=[DataRequired()])
    end_date = DateField('تاريخ النهاية', validators=[DataRequired()])
    
    export_format = SelectField('صيغة التصدير', choices=[
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('pdf', 'PDF')
    ], validators=[DataRequired()])
    
    submit = SubmitField('إنشاء التقرير')

class LiteraryReportForm(FlaskForm):
    report_type = SelectField('نوع التقرير', choices=[
        ('activities', 'تقرير الأنشطة'),
        ('events', 'تقرير الفعاليات'),
        ('courses', 'تقرير الدورات'),
        ('students', 'تقرير الطلاب'),
        ('teachers', 'تقرير المدرسين')
    ], validators=[DataRequired()])
    
    department = SelectField('القسم', choices=[
        ('all', 'جميع الأقسام'),
        ('academic', 'القسم الأكاديمي'),
        ('cultural', 'القسم الثقافي'),
        ('sports', 'القسم الرياضي'),
        ('social', 'القسم الاجتماعي')
    ], validators=[DataRequired()])
    
    start_date = DateField('تاريخ البداية', validators=[DataRequired()])
    end_date = DateField('تاريخ النهاية', validators=[DataRequired()])
    
    export_format = SelectField('صيغة التصدير', choices=[
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('pdf', 'PDF')
    ], validators=[DataRequired()])
    
    submit = SubmitField('إنشاء التقرير') 