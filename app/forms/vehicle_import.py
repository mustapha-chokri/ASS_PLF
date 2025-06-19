from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

class VehicleImportForm(FlaskForm):
    """نموذج استيراد السيارات من ملف إكسل"""
    file = FileField('ملف الإكسل', 
                    validators=[
                        FileRequired(message='يرجى اختيار ملف إكسل'),
                        FileAllowed(['xlsx', 'xls'], message='يرجى اختيار ملف إكسل صالح')
                    ])
    submit = SubmitField('استيراد') 