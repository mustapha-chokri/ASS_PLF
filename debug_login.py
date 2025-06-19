from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
import logging

def debug_login():
    app = create_app()
    with app.app_context():
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Find admin user
        admin = User.query.filter_by(username='admin').first()
        if admin:
            logger.info("Admin user found:")
            logger.info(f"Username: {admin.username}")
            logger.info(f"Email: {admin.email}")
            logger.info(f"Full Name: {admin.full_name}")
            logger.info(f"Is Admin: {admin.is_admin}")
            logger.info(f"Created At: {admin.created_at}")
            logger.info(f"Password Hash: {admin.password_hash}")
            
            # Test password
            test_password = 'admin123'
            logger.info(f"\nTesting password '{test_password}':")
            
            # Generate new hash for comparison
            new_hash = generate_password_hash(test_password)
            logger.info(f"New hash for 'admin123': {new_hash}")
            
            # Check password
            is_valid = admin.check_password(test_password)
            logger.info(f"Password is valid: {is_valid}")
            
            if not is_valid:
                logger.info("\nResetting password...")
                admin.set_password(test_password)
                db.session.commit()
                logger.info("Password has been reset!")
                
                # Verify new password
                is_valid = admin.check_password(test_password)
                logger.info(f"New password is valid: {is_valid}")
        else:
            logger.error("Admin user not found!")
            
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
            logger.info("\nNew admin user created!")
            logger.info("Username: admin")
            logger.info("Password: admin123")

if __name__ == '__main__':
    debug_login() 