# -*- coding: utf-8 -*- 
from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    # التحقق من وجود مستخدم مسؤول
    admin = User.query.filter_by(email='admin@example.com').first()
    if admin:
        print('المستخدم المسؤول موجود بالفعل')
    else:
        # إنشاء مستخدم مسؤول جديد
        admin = User(
            username='admin',
            email='admin@example.com',
            full_name='مدير النظام',
            role='admin',
            is_admin=True,
            is_active=True
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        print('تم إنشاء المستخدم المسؤول بنجاح') 