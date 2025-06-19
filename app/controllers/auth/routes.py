@auth_bp.route('/create-admin')
def create_admin():
    """إنشاء مستخدم مسؤول"""
    try:
        # التحقق من وجود مستخدم مسؤول
        admin = User.query.filter_by(email='admin@example.com').first()
        if admin:
            return 'المستخدم المسؤول موجود بالفعل'
        
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
        
        return 'تم إنشاء المستخدم المسؤول بنجاح'
    except Exception as e:
        db.session.rollback()
        return f'حدث خطأ: {str(e)}' 