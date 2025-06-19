from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    users = User.query.all()
    if users:
        print("المستخدمين الموجودين:")
        for user in users:
            print(f"الاسم: {user.username}, البريد الإلكتروني: {user.email}, مشرف: {user.is_admin}")
    else:
        print("لا يوجد مستخدمين في قاعدة البيانات!") 