from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from datetime import datetime
import logging

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    full_name = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # Increased length for hash
    role = db.Column(db.String(20), default='user', nullable=False)  # user, admin, editor, viewer
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Set password hash using werkzeug's generate_password_hash"""
        try:
            self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            logging.info(f"Password hash generated for user {self.username}")
        except Exception as e:
            logging.error(f"Error generating password hash: {str(e)}")
            raise
    
    def check_password(self, password):
        """Check password against hash using werkzeug's check_password_hash"""
        try:
            is_valid = check_password_hash(self.password_hash, password)
            logging.info(f"Password check for user {self.username}: {is_valid}")
            return is_valid
        except Exception as e:
            logging.error(f"Error checking password: {str(e)}")
            return False
    
    @classmethod
    def create_admin(cls, username, email, full_name, password):
        """Create a new admin user"""
        try:
            user = cls(
                username=username,
                email=email,
                full_name=full_name,
                role='admin',
                is_admin=True,
                is_active=True
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            logging.info(f"Admin user created: {username}")
            return user
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating admin user: {str(e)}")
            raise

@login_manager.user_loader
def load_user(id):
    """Load user by ID for Flask-Login"""
    try:
        user = User.query.get(int(id))
        if user:
            logging.info(f"User loaded: {user.username}")
        else:
            logging.warning(f"User not found with ID: {id}")
        return user
    except Exception as e:
        logging.error(f"Error loading user: {str(e)}")
        return None 