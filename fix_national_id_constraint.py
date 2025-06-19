import sqlite3
import os
from datetime import datetime

# المسار إلى قاعدة البيانات
DB_PATH = 'app/association.db'

# فتح اتصال بقاعدة البيانات
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("إنشاء جدول جديد بالتعديلات المطلوبة...")
# إنشاء جدول مؤقت بدون قيد NOT NULL على حقل national_id
cursor.execute("""
CREATE TABLE IF NOT EXISTS membership_applications_temp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    national_id VARCHAR(20),
    birth_date DATE,
    address VARCHAR(256),
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(120),
    profession VARCHAR(64),
    application_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL,
    notes TEXT,
    reviewed_by INTEGER,
    review_date DATETIME,
    application_token VARCHAR(64) UNIQUE
)
""")

# نسخ البيانات من الجدول القديم إلى الجدول المؤقت
print("نسخ البيانات من الجدول القديم...")
cursor.execute("""
INSERT INTO membership_applications_temp 
SELECT id, first_name, last_name, national_id, birth_date, address, phone, 
       email, profession, application_date, status, notes, reviewed_by, 
       review_date, application_token 
FROM membership_applications
""")

# حذف الجدول القديم وإعادة تسمية الجدول المؤقت
print("استبدال الجدول القديم بالجدول الجديد...")
cursor.execute("DROP TABLE membership_applications")
cursor.execute("ALTER TABLE membership_applications_temp RENAME TO membership_applications")

# حفظ التغييرات وإغلاق الاتصال
conn.commit()
print("تم إصلاح قيد NOT NULL على حقل national_id بنجاح!")
conn.close() 