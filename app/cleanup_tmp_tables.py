import sqlite3

conn = sqlite3.connect('app.db')
c = conn.cursor()
c.execute('DROP TABLE IF EXISTS _alembic_tmp_about')
conn.commit()
conn.close()
print("تم حذف الجدول المؤقت بنجاح.")
