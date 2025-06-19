from app import create_app, db
from app.models.user import User

def reset_admin_password():
    app = create_app()
    with app.app_context():
        # Find admin user
        admin = User.query.filter_by(username='admin').first()
        if admin:
            # Reset password
            admin.set_password('admin123')
            db.session.commit()
            print("Admin password has been reset successfully!")
            print("Username: admin")
            print("Password: admin123")
        else:
            print("Admin user not found!")

if __name__ == '__main__':
    reset_admin_password() 