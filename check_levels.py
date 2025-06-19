from app import create_app, db
from app.models.student import EducationalLevel

app = create_app()

with app.app_context():
    levels = EducationalLevel.query.order_by(EducationalLevel.order).all()
    
    if levels:
        print("المستويات الدراسية الموجودة:")
        for level in levels:
            print(f"الاسم: {level.name}, الترتيب: {level.order}, الوصف: {level.description}")
    else:
        print("لا توجد مستويات دراسية في قاعدة البيانات!")
        
        # إضافة بعض المستويات الافتراضية للاختبار
        print("إضافة مستويات دراسية افتراضية...")
        default_levels = [
            EducationalLevel(name="الروض", order=10, description="مرحلة ما قبل المدرسة"),
            EducationalLevel(name="المستوى الأول ابتدائي", order=20),
            EducationalLevel(name="المستوى الثاني ابتدائي", order=30),
            EducationalLevel(name="المستوى الثالث ابتدائي", order=40),
            EducationalLevel(name="المستوى الرابع ابتدائي", order=50),
            EducationalLevel(name="المستوى الخامس ابتدائي", order=60),
            EducationalLevel(name="المستوى السادس ابتدائي", order=70),
            EducationalLevel(name="الأولى إعدادي", order=80),
            EducationalLevel(name="الثانية إعدادي", order=90),
            EducationalLevel(name="الثالثة إعدادي", order=100)
        ]
        
        for level in default_levels:
            db.session.add(level)
        
        db.session.commit()
        print("تم إضافة المستويات الدراسية الافتراضية بنجاح!") 