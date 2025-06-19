from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    username = StringField('اسم المستخدم', 
        validators=[
            DataRequired(message='يرجى إدخال اسم المستخدم'),
            Length(min=3, max=64, message='يجب أن يكون طول اسم المستخدم بين 3 و 64 حرفاً')
        ],
        render_kw={"autocomplete": "username"}
    )
    password = PasswordField('كلمة المرور', 
        validators=[
            DataRequired(message='يرجى إدخال كلمة المرور'),
            Length(min=6, message='يجب أن تكون كلمة المرور 6 أحرف على الأقل')
        ],
        render_kw={"autocomplete": "current-password"}
    )
    remember_me = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if not user:
            raise ValidationError('اسم المستخدم غير موجود') 