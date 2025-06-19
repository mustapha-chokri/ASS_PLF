from app import create_app, db
from app.models.user import User
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash
import logging

def test_auth():
    app = create_app()
    with app.app_context():
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Drop and recreate users table
        User.__table__.drop(db.engine, checkfirst=True)
        User.__table__.create(db.engine)
        logger.info("Users table recreated")
        
        # Create admin user with direct password hash
        password = 'admin123'
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
        admin = User(
            username='admin',
            email='admin@example.com',
            full_name='System Administrator',
            password_hash=password_hash,
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        logger.info("Admin user created with direct password hash")
        
        # Verify admin user
        admin = User.query.filter_by(username='admin').first()
        if admin:
            logger.info("Admin user found:")
            logger.info(f"Username: {admin.username}")
            logger.info(f"Password Hash: {admin.password_hash}")
            
            # Test password directly
            is_valid = check_password_hash(admin.password_hash, password)
            logger.info(f"Direct password check: {is_valid}")
            
            # Test password through model
            is_valid = admin.check_password(password)
            logger.info(f"Model password check: {is_valid}")
            
            # Test login_user
            with app.test_request_context():
                login_success = login_user(admin)
                logger.info(f"login_user success: {login_success}")
        else:
            logger.error("Admin user not found!")

if __name__ == '__main__':
    test_auth() 