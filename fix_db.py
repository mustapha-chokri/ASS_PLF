import sqlite3

# فتح اتصال بقاعدة البيانات
conn = sqlite3.connect('app/association.db')
cursor = conn.cursor()

# التحقق من وجود العمود
cursor.execute("PRAGMA table_info(membership_applications)")
columns = [column[1] for column in cursor.fetchall()]

# إضافة العمود إذا لم يكن موجوداً
if 'application_token' not in columns:
    cursor.execute("ALTER TABLE membership_applications ADD COLUMN application_token TEXT")
    conn.commit()
    print('تم إضافة العمود application_token بنجاح')
else:
    print('العمود application_token موجود بالفعل')

# إغلاق الاتصال
conn.close() 