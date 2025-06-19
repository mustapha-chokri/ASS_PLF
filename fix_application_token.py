import sqlite3
import os
from datetime import datetime

# المسار إلى قاعدة البيانات
DB_PATH = 'app/association.db'

# فتح اتصال بقاعدة البيانات
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# نسخ بيانات الطلبات الحالية
print("جاري استرجاع البيانات الحالية...")
cursor.execute("SELECT * FROM membership_applications")
applications_data = cursor.fetchall()

# الحصول على أسماء الأعمدة
cursor.execute("PRAGMA table_info(membership_applications)")
columns_info = cursor.fetchall()
column_names = [column[1] for column in columns_info]

print(f"تم العثور على {len(applications_data)} طلبات")
print(f"أعمدة الجدول: {column_names}")

# إنشاء جدول مؤقت بالهيكل الصحيح
print("جاري إنشاء جدول مؤقت...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS membership_applications_temp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    national_id VARCHAR(20) NOT NULL,
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

# نقل البيانات إلى الجدول المؤقت
# نحتاج إلى تحديد مؤشرات الأعمدة بناءً على الأسماء
id_idx = column_names.index('id')
first_name_idx = column_names.index('first_name')
last_name_idx = column_names.index('last_name')
national_id_idx = column_names.index('national_id') if 'national_id' in column_names else None
birth_date_idx = column_names.index('birth_date') if 'birth_date' in column_names else None
address_idx = column_names.index('address') if 'address' in column_names else None
phone_idx = column_names.index('phone') if 'phone' in column_names else None
email_idx = column_names.index('email') if 'email' in column_names else None
profession_idx = column_names.index('profession') if 'profession' in column_names else None
application_date_idx = column_names.index('application_date') if 'application_date' in column_names else None
status_idx = column_names.index('status') if 'status' in column_names else None
notes_idx = column_names.index('notes') if 'notes' in column_names else None
reviewed_by_idx = column_names.index('reviewed_by') if 'reviewed_by' in column_names else None
review_date_idx = column_names.index('review_date') if 'review_date' in column_names else None
application_token_idx = column_names.index('application_token') if 'application_token' in column_names else None

print("جاري نقل البيانات إلى الجدول المؤقت...")
for app in applications_data:
    # تحضير البيانات مع التعامل مع القيم الناقصة
    data = {
        'id': app[id_idx],
        'first_name': app[first_name_idx],
        'last_name': app[last_name_idx],
        'national_id': app[national_id_idx] if national_id_idx is not None and national_id_idx < len(app) else None,
        'birth_date': app[birth_date_idx] if birth_date_idx is not None and birth_date_idx < len(app) else None,
        'address': app[address_idx] if address_idx is not None and address_idx < len(app) else None,
        'phone': app[phone_idx] if phone_idx is not None and phone_idx < len(app) else '',
        'email': app[email_idx] if email_idx is not None and email_idx < len(app) else None,
        'profession': app[profession_idx] if profession_idx is not None and profession_idx < len(app) else None,
        'application_date': app[application_date_idx] if application_date_idx is not None and application_date_idx < len(app) else datetime.now().strftime('%Y-%m-%d'),
        'status': app[status_idx] if status_idx is not None and status_idx < len(app) else 'pending',
        'notes': app[notes_idx] if notes_idx is not None and notes_idx < len(app) else None,
        'reviewed_by': app[reviewed_by_idx] if reviewed_by_idx is not None and reviewed_by_idx < len(app) else None,
        'review_date': app[review_date_idx] if review_date_idx is not None and review_date_idx < len(app) else None,
        'application_token': app[application_token_idx] if application_token_idx is not None and application_token_idx < len(app) else None
    }
    
    # إدراج البيانات في الجدول المؤقت
    cursor.execute("""
    INSERT INTO membership_applications_temp (
        id, first_name, last_name, national_id, birth_date, address, phone,
        email, profession, application_date, status, notes, reviewed_by,
        review_date, application_token
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['id'], data['first_name'], data['last_name'], data['national_id'], 
        data['birth_date'], data['address'], data['phone'], data['email'], 
        data['profession'], data['application_date'], data['status'], 
        data['notes'], data['reviewed_by'], data['review_date'], data['application_token']
    ))

# حفظ التغييرات
conn.commit()

print("جاري استبدال الجدول القديم بالجدول الجديد...")
# حذف الجدول القديم وإعادة تسمية الجدول المؤقت
cursor.execute("DROP TABLE membership_applications")
cursor.execute("ALTER TABLE membership_applications_temp RENAME TO membership_applications")

# تأكيد التغييرات وإغلاق الاتصال
conn.commit()
print("تم إصلاح جدول الطلبات بنجاح!")
conn.close() 