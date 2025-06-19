from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, DateField, SelectField, TextAreaField, FloatField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, Optional, Length, ValidationError, Regexp
from datetime import datetime

class StudentForm(FlaskForm):
    student_id = StringField('رقم التلميذ', validators=[DataRequired()])
    first_name = StringField('الاسم الشخصي', validators=[DataRequired()])
    last_name = StringField('النسب', validators=[DataRequired()])
    gender = SelectField('الجنس', choices=[
        ('male', 'ذكر'),
        ('female', 'أنثى')
    ], validators=[DataRequired()])
    massar_number = StringField('رقم مسار', validators=[Optional()])
    birth_date = DateField('تاريخ الازدياد', format='%Y-%m-%d', validators=[Optional()])
    educational_level = SelectField('المستوى الدراسي', validators=[DataRequired()])
    institution = StringField('المؤسسة', validators=[Optional()])
    monthly_fee = FloatField('مبلغ الاشتراك الشهري', validators=[DataRequired()])
    
    # Guardian information
    guardian_name = StringField('اسم ولي الأمر', validators=[DataRequired()])
    guardian_national_id = StringField('رقم البطاقة الوطنية لولي الأمر', validators=[Optional()])
    guardian_phone = StringField('رقم هاتف ولي الأمر', validators=[DataRequired()])
    guardian_email = StringField('البريد الإلكتروني لولي الأمر', validators=[Optional(), Email()])
    address = TextAreaField('العنوان', validators=[Optional()])
    
    # Files
    student_photo = FileField('صورة التلميذ', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'يجب أن تكون الصورة بصيغة JPG أو PNG فقط!')
    ])
    guardian_id_front = FileField('صورة البطاقة الوطنية لولي الأمر (الوجه الأمامي)', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'يجب أن تكون الصورة بصيغة JPG أو PNG أو PDF فقط!')
    ])
    guardian_id_back = FileField('صورة البطاقة الوطنية لولي الأمر (الوجه الخلفي)', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'يجب أن تكون الصورة بصيغة JPG أو PNG أو PDF فقط!')
    ])
    commitment_doc = FileField('صورة الالتزام الموقع', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'يجب أن يكون المستند بصيغة JPG أو PNG أو PDF فقط!')
    ])
    
    notes = TextAreaField('ملاحظات', validators=[Optional()])
    status = SelectField('الحالة', choices=[
        ('active', 'نشط'),
        ('inactive', 'غير نشط')
    ], validators=[DataRequired()])
    submit = SubmitField('حفظ')


class TransportSubscriptionForm(FlaskForm):
    student_id = SelectField('التلميذ', coerce=int, validators=[DataRequired()])
    month = SelectField('الشهر', choices=[
        (1, 'يناير'),
        (2, 'فبراير'),
        (3, 'مارس'),
        (4, 'أبريل'),
        (5, 'ماي'),
        (6, 'يونيو'),
        (7, 'يوليوز'),
        (8, 'غشت'),
        (9, 'شتنبر'),
        (10, 'أكتوبر'),
        (11, 'نونبر'),
        (12, 'دجنبر')
    ], coerce=int, validators=[DataRequired()])
    year = SelectField('السنة', coerce=int, validators=[DataRequired()])
    amount = FloatField('المبلغ', validators=[DataRequired()])
    payment_date = DateField('تاريخ الدفع', format='%Y-%m-%d', default=datetime.now().date())
    payment_method = SelectField('طريقة الدفع', choices=[
        ('cash', 'نقداً'),
        ('bank_transfer', 'تحويل بنكي'),
        ('check', 'شيك')
    ], validators=[DataRequired()])
    receipt_number = StringField('رقم الإيصال', validators=[Optional()])
    notes = TextAreaField('ملاحظات', validators=[Optional()])
    submit = SubmitField('حفظ')


class EducationalLevelForm(FlaskForm):
    name = StringField('المستوى الدراسي', validators=[DataRequired()])
    order = StringField('الترتيب', validators=[DataRequired()])
    description = TextAreaField('الوصف', validators=[Optional()])
    submit = SubmitField('حفظ')


class ImportStudentsForm(FlaskForm):
    excel_file = FileField('ملف Excel', validators=[
        DataRequired(),
        FileAllowed(['xlsx', 'xls'], 'يجب أن يكون الملف بصيغة Excel فقط!')
    ])
    submit = SubmitField('استيراد')


class ImportTransportSubscriptionsForm(FlaskForm):
    excel_file = FileField('ملف Excel', validators=[
        DataRequired(),
        FileAllowed(['xlsx', 'xls'], 'يجب أن يكون الملف بصيغة Excel فقط!')
    ])
    submit = SubmitField('استيراد')


class RegistrationLinkForm(FlaskForm):
    notes = TextAreaField('ملاحظات داخلية (اختياري)', validators=[Optional()])
    submit = SubmitField('إنشاء رابط التسجيل')


class StudentRegistrationForm(FlaskForm):
    # Student information
    first_name = StringField('الاسم الشخصي للتلميذ', validators=[DataRequired(), Length(min=2, max=100)])
    last_name = StringField('نسب التلميذ', validators=[DataRequired(), Length(min=2, max=100)])
    gender = SelectField('الجنس', choices=[
        ('male', 'ذكر'),
        ('female', 'أنثى')
    ], validators=[DataRequired()])
    birth_date = DateField('تاريخ الازدياد', format='%Y-%m-%d', validators=[Optional()])
    massar_number = StringField('رقم مسار', validators=[Optional(), Length(max=100)])
    educational_level = SelectField('المستوى الدراسي', validators=[DataRequired()])
    institution = StringField('المؤسسة', validators=[Optional(), Length(max=100)])
    
    # Guardian information
    guardian_name = StringField('اسم ولي الأمر', validators=[DataRequired(), Length(min=3, max=100)])
    guardian_national_id = StringField('رقم البطاقة الوطنية لولي الأمر', validators=[Optional(), Length(max=100)])
    guardian_phone = StringField('رقم هاتف ولي الأمر', validators=[
        DataRequired(),
        Length(min=8, max=20),
        Regexp(r'^\+?[\d\s\-()]+$', message='الرجاء إدخال رقم هاتف صحيح')
    ])
    guardian_email = StringField('البريد الإلكتروني لولي الأمر', validators=[Optional(), Email()])
    address = TextAreaField('العنوان', validators=[Optional()])
    
    # Files
    student_photo = FileField('صورة التلميذ', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'يجب أن تكون الصورة بصيغة JPG أو PNG فقط!')
    ])
    guardian_id_front = FileField('صورة البطاقة الوطنية لولي الأمر (الوجه الأمامي)', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'يجب أن تكون الصورة بصيغة JPG أو PNG أو PDF فقط!')
    ])
    guardian_id_back = FileField('صورة البطاقة الوطنية لولي الأمر (الوجه الخلفي)', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'يجب أن تكون الصورة بصيغة JPG أو PNG أو PDF فقط!')
    ])
    commitment_doc = FileField('صورة الالتزام الموقع', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'يجب أن يكون المستند بصيغة JPG أو PNG أو PDF فقط!')
    ])
    
    notes = TextAreaField('ملاحظات إضافية', validators=[Optional()])
    token = HiddenField('رمز التسجيل')
    submit = SubmitField('إرسال طلب التسجيل') 