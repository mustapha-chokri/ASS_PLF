from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Optional, NumberRange

class EducationalLevelForm(FlaskForm):
    name = StringField('المستوى الدراسي', validators=[DataRequired()])
    order = IntegerField('الترتيب', validators=[DataRequired(), NumberRange(min=1)])
    description = TextAreaField('الوصف', validators=[Optional()]) 