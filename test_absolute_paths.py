import os
from config import Config

def test_absolute_paths():
    """اختبار المسارات المطلقة"""
    print("=== اختبار المسارات المطلقة ===")
    
    # اختبار مسار قاعدة البيانات
    db_path = Config.DATABASE_PATH
    print(f"مسار قاعدة البيانات: {db_path}")
    print(f"المسار موجود: {os.path.exists(db_path)}")
    print(f"المسار قابل للكتابة: {os.access(os.path.dirname(db_path), os.W_OK)}")
    
    # اختبار مجلد التحميلات
    upload_path = Config.UPLOAD_FOLDER
    print(f"مجلد التحميلات: {upload_path}")
    print(f"المجلد موجود: {os.path.exists(upload_path)}")
    print(f"المجلد قابل للكتابة: {os.access(upload_path, os.W_OK)}")
    
    # اختبار مجلد الهجرات
    migrations_path = Config.MIGRATIONS_DIR
    print(f"مجلد الهجرات: {migrations_path}")
    print(f"المجلد موجود: {os.path.exists(migrations_path)}")
    
    # اختبار URI قاعدة البيانات
    print(f"URI قاعدة البيانات: {Config.SQLALCHEMY_DATABASE_URI}")
    
    print("\n=== انتهى الاختبار ===")

if __name__ == "__main__":
    test_absolute_paths() 