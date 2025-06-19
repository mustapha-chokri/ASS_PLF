from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models.user import User
from app.auth.security import is_password_strong

class LoginForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired()])
    password = PasswordField('كلمة المرور', validators=[DataRequired()])
    remember_me = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')

class RegistrationForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired()])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    full_name = StringField('الاسم الكامل', validators=[DataRequired()])
    password = PasswordField('كلمة المرور', validators=[DataRequired()])
    password2 = PasswordField(
        'تأكيد كلمة المرور', validators=[DataRequired(), EqualTo('password')]
    )
    is_admin = BooleanField('مشرف النظام')
    submit = SubmitField('تسجيل')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('هذا الاسم مستخدم بالفعل، الرجاء اختيار اسم آخر.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('هذا البريد الإلكتروني مسجل بالفعل، الرجاء استخدام بريد آخر.')
            
    def validate_password(self, password):
        if not is_password_strong(password.data):
            raise ValidationError('كلمة المرور يجب أن تحتوي على 8 أحرف على الأقل، وتتضمن حروف كبيرة وصغيرة وأرقام ورموز خاصة.') 