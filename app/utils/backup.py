import os
import shutil
from datetime import datetime
from flask import current_app
import sqlite3

def create_backup():
    """
    إنشاء نسخة احتياطية من قاعدة البيانات
    """
    try:
        # إنشاء مجلد النسخ الاحتياطي إذا لم يكن موجوداً
        backup_dir = os.path.join(current_app.root_path, 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # إنشاء اسم الملف مع التاريخ والوقت
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'backup_{timestamp}.db')
        
        # نسخ قاعدة البيانات
        db_path = os.path.join(current_app.instance_path, 'app.db')
        shutil.copy2(db_path, backup_file)
        
        # الاحتفاظ فقط بأحدث 5 نسخ احتياطية
        cleanup_old_backups(backup_dir)
        
        return True, f'تم إنشاء النسخة الاحتياطية بنجاح: {backup_file}'
    except Exception as e:
        return False, f'حدث خطأ أثناء إنشاء النسخة الاحتياطية: {str(e)}'

def cleanup_old_backups(backup_dir, keep_count=5):
    """
    حذف النسخ الاحتياطية القديمة
    """
    try:
        backups = []
        for file in os.listdir(backup_dir):
            if file.startswith('backup_') and file.endswith('.db'):
                file_path = os.path.join(backup_dir, file)
                backups.append((file_path, os.path.getmtime(file_path)))
        
        # ترتيب النسخ الاحتياطية حسب تاريخ التعديل
        backups.sort(key=lambda x: x[1], reverse=True)
        
        # حذف النسخ القديمة
        for backup in backups[keep_count:]:
            os.remove(backup[0])
            
        return True
    except Exception as e:
        return False

def restore_backup(backup_file):
    """
    استعادة نسخة احتياطية
    """
    try:
        db_path = os.path.join(current_app.instance_path, 'app.db')
        
        # التحقق من وجود النسخة الاحتياطية
        if not os.path.exists(backup_file):
            return False, 'النسخة الاحتياطية غير موجودة'
        
        # نسخ النسخة الاحتياطية إلى قاعدة البيانات
        shutil.copy2(backup_file, db_path)
        
        return True, 'تم استعادة النسخة الاحتياطية بنجاح'
    except Exception as e:
        return False, f'حدث خطأ أثناء استعادة النسخة الاحتياطية: {str(e)}' 