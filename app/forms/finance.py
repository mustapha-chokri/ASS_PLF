from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from app.models.finance import IncomeSource # تأكد من مسار الاستيراد الصحيح لمصدر المدخول
from app.models.user import User # تأكد من مسار الاستيراد الصحيح للمستخدمين
from app import db

class AddIncomeForm(FlaskForm):
    operation = StringField('العملية', validators=[DataRequired(), Length(max=128)])
    amount = FloatField('المبلغ', validators=[DataRequired(), NumberRange(min=0.01)])
    income_date = DateField('التاريخ', format='%Y-%m-%d', validators=[DataRequired()])
    payment_type = SelectField('نوع الدفع', choices=[('نقدي', 'نقدي'), ('شيك', 'شيك'), ('تحويل بنكي', 'تحويل بنكي')], validators=[DataRequired()])
    income_source_id = SelectField('المصدر', coerce=int, validators=[DataRequired()])
    responsible_id = SelectField('المسؤول', coerce=int, validators=[DataRequired()])
    notes = TextAreaField('ملاحظات', validators=[Length(max=500)], render_kw={"rows": 3})
    submit = SubmitField('حفظ')

    def __init__(self, *args, **kwargs):
        super(AddIncomeForm, self).__init__(*args, **kwargs)
        # ملء خيارات مصادر المدخول والمستخدمين
        with db.engine.connect() as conn:
             # استخدام text() مع SQLAlchemy 2.0+ لتجنب التحذيرات
            sources = conn.execute(db.text("SELECT id, name FROM income_sources")).fetchall()
            users_list = conn.execute(db.text("SELECT id, full_name FROM users")).fetchall()

        self.income_source_id.choices = [(s[0], s[1]) for s in sources]
        self.responsible_id.choices = [(u[0], u[1]) for u in users_list] 