from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
import logging

def fix_login_issue():
    """إصلاح مشكلة تسجيل الدخول"""
    app = create_app()
    
    with app.app_context():
        # إعداد التسجيل
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        logger.info("=== بدء إصلاح مشكلة تسجيل الدخول ===")
        
        # البحث عن المستخدم admin
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            logger.info(f"تم العثور على المستخدم: {admin.username}")
            logger.info(f"البريد الإلكتروني: {admin.email}")
            logger.info(f"الاسم الكامل: {admin.full_name}")
            logger.info(f"هل هو مدير: {admin.is_admin}")
            logger.info(f"هل نشط: {admin.is_active}")
            
            # اختبار كلمة المرور الحالية
            test_password = 'admin123'
            current_valid = admin.check_password(test_password)
            logger.info(f"كلمة المرور الحالية صحيحة: {current_valid}")
            
            if not current_valid:
                logger.info("إعادة تعيين كلمة المرور...")
                # إعادة تعيين كلمة المرور
                admin.set_password(test_password)
                db.session.commit()
                logger.info("تم إعادة تعيين كلمة المرور!")
                
                # التحقق من كلمة المرور الجديدة
                new_valid = admin.check_password(test_password)
                logger.info(f"كلمة المرور الجديدة صحيحة: {new_valid}")
                
                if new_valid:
                    logger.info("✅ تم إصلاح مشكلة تسجيل الدخول بنجاح!")
                    logger.info("اسم المستخدم: admin")
                    logger.info("كلمة المرور: admin123")
                else:
                    logger.error("❌ فشل في إصلاح كلمة المرور!")
            else:
                logger.info("✅ كلمة المرور صحيحة بالفعل!")
                
        else:
            logger.warning("لم يتم العثور على المستخدم admin، إنشاء مستخدم جديد...")
            
            # إنشاء مستخدم admin جديد
            admin = User(
                username='admin',
                email='admin@example.com',
                full_name='مدير النظام',
                is_admin=True,
                is_active=True
            )
            admin.set_password('admin123')
            
            db.session.add(admin)
            db.session.commit()
            
            logger.info("✅ تم إنشاء مستخدم admin جديد!")
            logger.info("اسم المستخدم: admin")
            logger.info("كلمة المرور: admin123")
        
        logger.info("=== انتهى إصلاح مشكلة تسجيل الدخول ===")

if __name__ == "__main__":
    fix_login_issue() 