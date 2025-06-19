import sqlite3

conn = sqlite3.connect('data/app.db')
c = conn.cursor()

print("الجداول قبل الحذف:")
for row in c.execute("SELECT name FROM sqlite_master WHERE type='table';"):
    print(row[0])

c.execute('DROP TABLE IF EXISTS _alembic_tmp_about')
conn.commit()

print("\nالجداول بعد الحذف:")
for row in c.execute("SELECT name FROM sqlite_master WHERE type='table';"):
    print(row[0])

conn.close()
print("\nتم حذف الجدول المؤقت _alembic_tmp_about بنجاح إذا كان موجودًا.") 