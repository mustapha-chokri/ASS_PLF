from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, PasswordField, SubmitField, SelectField, EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, Regexp
from app.models.user import User

class SettingForm(FlaskForm):
    # إعدادات الموقع
    site_name = StringField('اسم الموقع', validators=[DataRequired(), Length(max=100)])
    site_description = TextAreaField('وصف الموقع', validators=[Optional(), Length(max=500)])
    footer_text = StringField('نص التذييل', validators=[Optional(), Length(max=100)])
    
    # معلومات الاتصال
    contact_email = StringField('البريد الإلكتروني للتواصل', validators=[Optional(), Email(), Length(max=100)])
    contact_phone = StringField('رقم الهاتف للتواصل', validators=[Optional(), Length(max=20)])
    address = TextAreaField('العنوان', validators=[Optional(), Length(max=200)])
    
    # إعدادات النظام
    maintenance_mode = BooleanField('وضع الصيانة')
    allow_registration = BooleanField('السماح بالتسجيل')
    default_language = SelectField('اللغة الافتراضية', choices=[
        ('ar', 'العربية'),
        ('en', 'English'),
        ('fr', 'Français')
    ])
    timezone = SelectField('المنطقة الزمنية', choices=[
        ('Africa/Algiers', 'الجزائر'),
        ('Africa/Cairo', 'القاهرة'),
        ('Africa/Casablanca', 'الدار البيضاء'),
        ('Africa/Tunis', 'تونس'),
        ('Europe/Paris', 'باريس'),
        ('Europe/London', 'لندن')
    ])
    
    # زر الحفظ
    submit = SubmitField('حفظ الإعدادات')

class UserForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[
        DataRequired(message='اسم المستخدم مطلوب'),
        Length(min=3, max=50, message='يجب أن يكون طول اسم المستخدم بين 3 و 50 حرفاً'),
        Regexp(r'^[\w.@+-]+$', message='اسم المستخدم يمكن أن يحتوي فقط على أحرف وأرقام و @/./+/-/_')
    ])
    email = EmailField('البريد الإلكتروني', validators=[
        DataRequired(message='البريد الإلكتروني مطلوب'),
        Email(message='يرجى إدخال بريد إلكتروني صحيح'),
        Length(max=120, message='البريد الإلكتروني طويل جداً')
    ])
    full_name = StringField('الاسم الكامل', validators=[
        DataRequired(message='الاسم الكامل مطلوب'),
        Length(max=100, message='الاسم الكامل طويل جداً')
    ])
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(message='كلمة المرور مطلوبة'),
        Length(min=8, message='يجب أن تكون كلمة المرور 8 أحرف على الأقل'),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$',
               message='يجب أن تحتوي كلمة المرور على حرف واحد على الأقل ورقم واحد على الأقل')
    ])
    password2 = PasswordField('تأكيد كلمة المرور', validators=[
        DataRequired(message='تأكيد كلمة المرور مطلوب'),
        EqualTo('password', message='كلمات المرور غير متطابقة')
    ])
    role = SelectField('الدور', choices=[
        ('user', 'مستخدم'),
        ('admin', 'مدير'),
        ('editor', 'محرر'),
        ('viewer', 'مشاهد')
    ], validators=[DataRequired(message='الدور مطلوب')])
    is_active = BooleanField('نشط', default=True)
    is_admin = BooleanField('مدير النظام')
    submit = SubmitField('حفظ')
    
    def __init__(self, original_username=None, original_email=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
        
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('اسم المستخدم مستخدم بالفعل')
                
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('البريد الإلكتروني مستخدم بالفعل')

class NotificationForm(FlaskForm):
    email_notifications = BooleanField('تفعيل إشعارات البريد الإلكتروني')
    sms_notifications = BooleanField('تفعيل إشعارات الرسائل القصيرة')
    notification_sound = BooleanField('تفعيل صوت الإشعارات')
    notification_desktop = BooleanField('تفعيل إشعارات سطح المكتب')
    notification_email = StringField('البريد الإلكتروني للإشعارات', validators=[
        Optional(),
        Email(message='يرجى إدخال بريد إلكتروني صحيح')
    ])
    notification_sms = StringField('رقم الجوال للإشعارات', validators=[
        Optional(),
        Length(min=10, max=15, message='يرجى إدخال رقم جوال صحيح')
    ])
    submit = SubmitField('حفظ الإعدادات') 