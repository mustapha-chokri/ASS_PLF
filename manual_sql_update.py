import sqlite3

db_path = 'data/app.db'

conn = sqlite3.connect(db_path)
c = conn.cursor()

# إنشاء جدول About
c.execute('''
CREATE TABLE IF NOT EXISTS about (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    logo TEXT,
    goals TEXT,
    principles TEXT,
    bylaws_text TEXT,
    bylaws_file TEXT,
    legal_doc TEXT,
    hq_image TEXT,
    created_at DATETIME,
    updated_at DATETIME
)
''')

# إنشاء جدول BoardMember
c.execute('''
CREATE TABLE IF NOT EXISTS board_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    position TEXT NOT NULL,
    join_date DATE,
    mandate_period TEXT,
    image TEXT,
    card_data TEXT,
    nationality TEXT,
    family_status TEXT,
    father_name TEXT,
    mother_name TEXT,
    national_id TEXT,
    address TEXT,
    job TEXT,
    birth_place TEXT,
    birth_date DATE,
    created_at DATETIME,
    updated_at DATETIME
)
''')

# إنشاء جدول Mandate
c.execute('''
CREATE TABLE IF NOT EXISTS mandates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    created_at DATETIME,
    updated_at DATETIME
)
''')

conn.commit()
conn.close()
print('تم إنشاء الجداول الجديدة مباشرة في قاعدة البيانات data/app.db بنجاح.') 