from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DateField, SelectField, FloatField
from wtforms.validators import DataRequired, Email, Optional, Length, ValidationError
from app.models.member import Member
from datetime import datetime

class MemberForm(FlaskForm):
    first_name = StringField('الاسم', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('النسب', validators=[DataRequired(), Length(max=64)])
    national_id = StringField('رقم البطاقة الوطنية', validators=[DataRequired(), Length(max=20)])
    birth_date = DateField('تاريخ الميلاد', validators=[Optional()])
    address = StringField('العنوان', validators=[Optional(), Length(max=256)])
    city = StringField('المدينة', validators=[Optional(), Length(max=64)])
    phone = StringField('الهاتف', validators=[Optional(), Length(max=15)])
    email = StringField('البريد الإلكتروني', validators=[Optional(), Email(), Length(max=120)])
    profession = StringField('المهنة', validators=[Optional(), Length(max=64)])
    join_date = DateField('تاريخ الانخراط', validators=[DataRequired()], default=datetime.now)
    status = SelectField('الحالة', choices=[
        ('active', 'نشط'),
        ('inactive', 'غير نشط'),
        ('suspended', 'معلق')
    ], default='active')
    photo = FileField('الصورة الشخصية', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'الصور فقط!')
    ])
    notes = TextAreaField('ملاحظات', validators=[Optional()])
    
    def validate_national_id(self, national_id):
        member = Member.query.filter_by(national_id=national_id.data).first()
        if member and (not hasattr(self, 'id') or member.id != self.id):
            raise ValidationError('رقم البطاقة الوطنية مسجل لعضو آخر.')

class MembershipApplicationForm(FlaskForm):
    first_name = StringField('الاسم', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('النسب', validators=[DataRequired(), Length(max=64)])
    national_id = StringField('رقم البطاقة الوطنية', validators=[DataRequired(), Length(max=20)])
    birth_date = DateField('تاريخ الميلاد', validators=[Optional()])
    address = StringField('العنوان', validators=[Optional(), Length(max=256)])
    phone = StringField('الهاتف', validators=[DataRequired(), Length(max=15)])
    email = StringField('البريد الإلكتروني', validators=[Optional(), Email(), Length(max=120)])
    profession = StringField('المهنة', validators=[Optional(), Length(max=64)])
    notes = TextAreaField('ملاحظات إضافية', validators=[Optional()])

class SubscriptionForm(FlaskForm):
    year = SelectField('السنة', coerce=int, validators=[DataRequired()])
    amount = FloatField('المبلغ', validators=[DataRequired()])
    payment_date = DateField('تاريخ الدفع', validators=[DataRequired()], default=datetime.now)
    payment_method = SelectField('طريقة الدفع', choices=[
        ('cash', 'نقداً'),
        ('bank_transfer', 'تحويل بنكي'),
        ('check', 'شيك'),
        ('other', 'أخرى')
    ], default='cash')
    receipt_number = StringField('رقم الإيصال', validators=[Optional(), Length(max=64)])
    notes = TextAreaField('ملاحظات', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(SubscriptionForm, self).__init__(*args, **kwargs)
        # Generate a list of years (current year and 5 years back)
        current_year = datetime.now().year
        self.year.choices = [(y, str(y)) for y in range(current_year-5, current_year+2)] 