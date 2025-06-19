import sqlite3

def delete_temp_table():
    try:
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect('instance/app.db')
        cursor = conn.cursor()
        
        # حذف الجدول المؤقت إذا كان موجوداً
        cursor.execute('DROP TABLE IF EXISTS _alembic_tmp_vehicles')
        
        # حفظ التغييرات
        conn.commit()
        print("تم حذف الجدول المؤقت بنجاح")
        
    except Exception as e:
        print(f"حدث خطأ: {str(e)}")
    finally:
        # إغلاق الاتصال
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    delete_temp_table() 