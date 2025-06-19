from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SubmitField, FileField, SelectField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf.file import FileAllowed

class AboutForm(FlaskForm):
    title = StringField('اسم الجمعية', validators=[DataRequired()])
    content = TextAreaField('نبذة عن الجمعية', validators=[DataRequired()])
    logo = FileField('شعار الجمعية', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'svg'], 'الصور فقط!'), Optional()])
    goals = TextAreaField('الأهداف', validators=[Optional()])
    principles = TextAreaField('المبادئ', validators=[Optional()])
    bylaws_text = TextAreaField('نص القانون الأساسي', validators=[Optional()])
    bylaws_file = FileField('ملف القانون الأساسي', validators=[FileAllowed(['pdf', 'doc', 'docx'], 'ملفات PDF أو Word فقط!'), Optional()])
    legal_doc = FileField('الوصل القانوني النهائي', validators=[FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF أو صورة فقط!'), Optional()])
    hq_image = FileField('صورة مقر الجمعية', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'الصور فقط!'), Optional()])
    submit = SubmitField('حفظ التعديلات')

class BoardMemberForm(FlaskForm):
    first_name = StringField('الاسم الشخصي', validators=[DataRequired()])
    last_name = StringField('الاسم العائلي', validators=[DataRequired()])
    position = StringField('الصفة داخل المكتب', validators=[DataRequired()])
    join_date = DateField('تاريخ الانخراط', format='%Y-%m-%d', validators=[Optional()])
    mandate_id = SelectField('فترة الانتداب', coerce=int, validators=[DataRequired(message='اختيار فترة الانتداب إجباري')])
    image = FileField('صورة العضو', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'الصور فقط!'), Optional()])
    nationality = StringField('الجنسية', validators=[Optional()])
    family_status = StringField('الحالة العائلية', validators=[Optional()])
    father_name = StringField('اسم الأب', validators=[Optional()])
    mother_name = StringField('اسم الأم', validators=[Optional()])
    national_id = StringField('رقم البطاقة الوطنية', validators=[Optional()])
    address = StringField('العنوان', validators=[Optional()])
    job = StringField('المهنة', validators=[Optional()])
    birth_place = StringField('مكان الازدياد', validators=[Optional()])
    birth_date = DateField('تاريخ الازدياد', format='%Y-%m-%d', validators=[Optional()])
    card_data = TextAreaField('بيانات إضافية', validators=[Optional()])
    import_file = FileField('استيراد أعضاء المكتب (Excel/CSV)', validators=[FileAllowed(['csv', 'xlsx'], 'ملفات Excel أو CSV فقط!'), Optional()])
    submit = SubmitField('حفظ')
    export = SubmitField('تصدير الأعضاء')

class MandateForm(FlaskForm):
    title = StringField('العنوان', validators=[
        DataRequired(message='هذا الحقل مطلوب'),
        Length(min=3, max=100, message='يجب أن يكون العنوان بين 3 و 100 حرف')
    ])
    start_date = DateField('تاريخ البداية', validators=[
        DataRequired(message='هذا الحقل مطلوب')
    ])
    end_date = DateField('تاريخ النهاية', validators=[
        Optional()
    ])
    description = TextAreaField('الوصف', validators=[
        DataRequired(message='هذا الحقل مطلوب'),
        Length(min=10, message='يجب أن يكون الوصف على الأقل 10 أحرف')
    ])
    submit = SubmitField('حفظ') 