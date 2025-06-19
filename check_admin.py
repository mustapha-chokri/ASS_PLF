from app import create_app, db
from app.models.user import User
from sqlalchemy import text

def check_admin():
    app = create_app()
    with app.app_context():
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user found:")
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Full Name: {admin.full_name}")
            print(f"Is Admin: {admin.is_admin}")
            print(f"Created At: {admin.created_at}")
            print(f"Last Login: {admin.last_login}")
        else:
            print("Admin user not found!")
            
            # Create new admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                full_name='System Administrator',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("\nNew admin user created!")
            print("Username: admin")
            print("Password: admin123")

if __name__ == '__main__':
    check_admin() 