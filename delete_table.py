import sqlite3

def delete_vehicles_table():
    try:
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect('instance/app.db')
        cursor = conn.cursor()
        
        # حذف الجدول إذا كان موجوداً
        cursor.execute('DROP TABLE IF EXISTS vehicles')
        
        # حفظ التغييرات
        conn.commit()
        print("تم حذف جدول vehicles بنجاح")
        
    except Exception as e:
        print(f"حدث خطأ: {str(e)}")
    finally:
        # إغلاق الاتصال
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    delete_vehicles_table() 