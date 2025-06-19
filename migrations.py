from app import create_app, db
from app.models.student import PendingStudent

app = create_app()

def create_tables():
    """Create database tables if they don't exist"""
    with app.app_context():
        db.create_all()
        print("Tables created successfully!")

if __name__ == "__main__":
    create_tables() 