from app import create_app, db
from app.models.user import User
from werkzeug.security import check_password_hash

def test_login():
    app = create_app()
    with app.app_context():
        # Find admin user
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user found:")
            print(f"Username: {admin.username}")
            print(f"Password hash: {admin.password_hash}")
            
            # Test password
            test_password = 'admin123'
            is_valid = admin.check_password(test_password)
            print(f"\nTesting password '{test_password}':")
            print(f"Password is valid: {is_valid}")
            
            # If password is not valid, reset it
            if not is_valid:
                print("\nResetting password...")
                admin.set_password(test_password)
                db.session.commit()
                print("Password has been reset!")
                
                # Verify new password
                is_valid = admin.check_password(test_password)
                print(f"New password is valid: {is_valid}")
        else:
            print("Admin user not found!")

if __name__ == '__main__':
    test_login() 