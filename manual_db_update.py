from app import create_app, db
from app.models.about import About, BoardMember, Mandate
from app.models.user import User

app = create_app()

with app.app_context():
    db.create_all()
    print('تم إنشاء الجداول الجديدة أو تحديثها بنجاح دون فقدان البيانات القديمة.') 