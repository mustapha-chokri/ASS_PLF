import sqlite3
try:
    conn = sqlite3.connect('data/app.db')
    print('تم فتح القاعدة بنجاح')
    conn.close()
except Exception as e:
    print(f'فشل فتح القاعدة: {e}') 