import sqlite3

# فتح اتصال بقاعدة البيانات
conn = sqlite3.connect('app/association.db')
cursor = conn.cursor()

# التحقق من وجود الجدول
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='membership_applications'")
if cursor.fetchone():
    # طباعة معلومات أعمدة الجدول
    cursor.execute("PRAGMA table_info(membership_applications)")
    columns = cursor.fetchall()
    print("معلومات أعمدة جدول membership_applications:")
    for column in columns:
        print(f"ID: {column[0]}, اسم: {column[1]}, نوع: {column[2]}, nullable: {column[3]}, default: {column[4]}, pk: {column[5]}")
else:
    print("الجدول membership_applications غير موجود!")

# إغلاق الاتصال
conn.close() 