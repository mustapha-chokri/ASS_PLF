import os
import sqlite3

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'test.db')
print(f'المسار النهائي لقاعدة البيانات: {db_path}')

# فحص صلاحيات المجلد
print(f'صلاحية الكتابة على المجلد: {os.access(basedir, os.W_OK)}')

try:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)')
    conn.commit()
    conn.close()
    print('تم إنشاء قاعدة البيانات test.db بنجاح.')
except Exception as e:
    print(f'حدث خطأ: {e}') 