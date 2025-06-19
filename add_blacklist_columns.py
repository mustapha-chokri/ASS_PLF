from app import create_app, db
from app.models.student import Student

app = create_app()

with app.app_context():
    # إضافة الأعمدة المفقودة
    with db.engine.begin() as conn:
        conn.execute('ALTER TABLE students ADD COLUMN is_blacklisted BOOLEAN DEFAULT FALSE')
        conn.execute('ALTER TABLE students ADD COLUMN blacklist_reason TEXT')
        conn.execute('ALTER TABLE students ADD COLUMN blacklist_duration INTEGER')
        conn.execute('ALTER TABLE students ADD COLUMN blacklist_start_date DATE')
        conn.execute('ALTER TABLE students ADD COLUMN blacklist_end_date DATE')
    
    print("تمت إضافة أعمدة القائمة السوداء بنجاح!") 