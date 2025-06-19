from app import create_app, db
from app.models.user import User
from sqlalchemy import text
from werkzeug.security import generate_password_hash

def recreate_admin():
    app = create_app()
    with app.app_context():
        # Drop the users table
        with db.engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS users"))
            conn.commit()
        
        # Create the users table
        User.__table__.create(db.engine)
        
        # Create new admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        
        # Verify admin user
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user created successfully!")
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Full Name: {admin.full_name}")
            print(f"Is Admin: {admin.is_admin}")
            
            # Test password
            is_valid = admin.check_password('admin123')
            print(f"\nPassword 'admin123' is valid: {is_valid}")
        else:
            print("Failed to create admin user!")

if __name__ == '__main__':
    recreate_admin() 