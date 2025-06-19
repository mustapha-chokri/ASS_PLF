from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, IntegerField, FloatField, DateField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class VehicleForm(FlaskForm):
    """نموذج إضافة/تعديل السيارة"""
    registration_number = StringField('رقم التسجيل', validators=[DataRequired(), Length(min=1, max=20)])
    vehicle_type = StringField('نوع المركبة', validators=[DataRequired(), Length(min=1, max=50)])
    brand = StringField('العلامة التجارية', validators=[Optional(), Length(max=50)])
    model = StringField('الموديل', validators=[DataRequired(), Length(min=1, max=50)])
    year = StringField('سنة الصنع', validators=[DataRequired(), Length(min=4, max=4)])
    capacity = IntegerField('السعة', validators=[Optional(), NumberRange(min=1)])
    status = SelectField('الحالة', 
                        choices=[
                            ('active', 'نشط'),
                            ('maintenance', 'في الصيانة'),
                            ('out_of_service', 'خارج الخدمة')
                        ],
                        validators=[DataRequired()])
    purchase_price = FloatField('سعر الشراء', validators=[Optional(), NumberRange(min=0)])
    purchase_date = DateField('تاريخ الشراء', validators=[Optional()])
    registration_expiry = DateField('تاريخ انتهاء التسجيل', validators=[Optional()])
    insurance_expiry = DateField('تاريخ انتهاء التأمين', validators=[Optional()])
    inspection_expiry = DateField('تاريخ انتهاء الفحص', validators=[Optional()])
    driving_license_expiry = DateField('تاريخ انتهاء رخصة القيادة', validators=[Optional()])
    current_mileage = IntegerField('المسافة المقطوعة', validators=[Optional(), NumberRange(min=0)])
    next_maintenance_mileage = IntegerField('المسافة للصيانة القادمة', validators=[Optional(), NumberRange(min=0)])
    next_maintenance_type = StringField('نوع الصيانة القادمة', validators=[Optional(), Length(max=50)])
    notes = TextAreaField('ملاحظات', validators=[Optional()])
    submit = SubmitField('حفظ')

class VehicleImportForm(FlaskForm):
    """نموذج استيراد السيارات"""
    file = FileField('ملف Excel', validators=[
        FileRequired(),
        FileAllowed(['xlsx'], 'يرجى اختيار ملف Excel (.xlsx)')
    ])
    submit = SubmitField('استيراد') 