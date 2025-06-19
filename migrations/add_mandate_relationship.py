"""
ترحيل قاعدة البيانات لإضافة علاقة فترة الانتداب
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def upgrade():
    """إضافة حقل mandate_id إلى جدول board_members"""
    app = create_app()
    with app.app_context():
        try:
            # إضافة العمود الجديد
            db.session.execute(text("""
                ALTER TABLE board_members 
                ADD COLUMN mandate_id INTEGER 
                REFERENCES mandates(id)
            """))
            db.session.commit()
            print("تم إضافة حقل mandate_id بنجاح")
        except Exception as e:
            db.session.rollback()
            print(f"خطأ في إضافة الحقل: {e}")

def downgrade():
    """إزالة حقل mandate_id من جدول board_members"""
    app = create_app()
    with app.app_context():
        try:
            db.session.execute(text("""
                ALTER TABLE board_members 
                DROP COLUMN mandate_id
            """))
            db.session.commit()
            print("تم إزالة حقل mandate_id بنجاح")
        except Exception as e:
            db.session.rollback()
            print(f"خطأ في إزالة الحقل: {e}")

if __name__ == "__main__":
    print("بدء ترحيل قاعدة البيانات...")
    upgrade()
    print("اكتمل الترحيل") 