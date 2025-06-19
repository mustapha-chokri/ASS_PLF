from app import create_app, db
from app.models.user import User

def check_admin_user():
    app = create_app()
    with app.app_context():
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Admin user does not exist!")
            return

        print("Admin user found:")
        print(f"Username: {admin.username}")
        print(f"Email: {admin.email}")
        print(f"Full Name: {admin.full_name}")
        print(f"Is Admin: {admin.is_admin}")
        
        # Test password
        test_password = 'admin123'
        if admin.check_password(test_password):
            print("\nPassword verification successful!")
        else:
            print("\nPassword verification failed!")
            print("Current password hash:", admin.password_hash)

if __name__ == '__main__':
    check_admin_user() 