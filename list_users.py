from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    users = User.query.all()
    if users:
        print("قائمة المستخدمين (الاسم الكامل):")
        for user in users:
            print(user.full_name)
    else:
        print("لا يوجد مستخدمون في قاعدة البيانات.") 