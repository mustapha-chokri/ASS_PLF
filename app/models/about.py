from app import db
from datetime import datetime

class About(db.Model):
    __tablename__ = 'about'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    logo = db.Column(db.String(255))  # مسار الشعار
    goals = db.Column(db.Text)        # الأهداف
    principles = db.Column(db.Text)   # المبادئ
    bylaws_text = db.Column(db.Text)  # نص القانون الأساسي
    bylaws_file = db.Column(db.String(255))  # ملف القانون الأساسي
    legal_doc = db.Column(db.String(255))    # الوصل القانوني النهائي
    hq_image = db.Column(db.String(255))     # صورة مقر الجمعية
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<About {self.title}>'

class BoardMember(db.Model):
    __tablename__ = 'board_members'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)   # الاسم الشخصي
    last_name = db.Column(db.String(100), nullable=False)    # الاسم العائلي
    position = db.Column(db.String(100), nullable=False)     # الصفة داخل المكتب
    join_date = db.Column(db.Date)                           # تاريخ الانخراط
    mandate_period = db.Column(db.String(100))               # فترة الانتداب (للتوافق مع البيانات الموجودة)
    mandate_id = db.Column(db.Integer, db.ForeignKey('mandates.id'), nullable=True)  # ربط بفترة الانتداب
    image = db.Column(db.String(255))                        # صورة العضو
    card_data = db.Column(db.Text)                           # بيانات إضافية للبطاقة
    nationality = db.Column(db.String(50))                   # الجنسية
    family_status = db.Column(db.String(50))                 # الحالة العائلية
    father_name = db.Column(db.String(100))                  # اسم الأب
    mother_name = db.Column(db.String(100))                  # اسم الأم
    national_id = db.Column(db.String(50))                   # رقم البطاقة الوطنية
    address = db.Column(db.String(255))                      # العنوان
    job = db.Column(db.String(100))                          # المهنة
    birth_place = db.Column(db.String(100))                  # مكان الازدياد
    birth_date = db.Column(db.Date)                          # تاريخ الازدياد
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقة مع فترة الانتداب
    mandate = db.relationship('Mandate', backref='board_members')

    def __repr__(self):
        return f'<BoardMember {self.first_name} {self.last_name}>'

class Mandate(db.Model):
    __tablename__ = 'mandates'
    
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Mandate {self.title}>' 