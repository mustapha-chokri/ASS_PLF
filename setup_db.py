import os
from app import create_app, db
from app.models.finance import (
    Income, IncomeSource,
    Expense, ExpenseType,
    CashBox, BankAccount, Transfer
)
from app.models.user import User
from app.models.student import Student, TransportSubscription, EducationalLevel, Program, StudentEnrollment, PendingStudent
from app.models.member import Member, MembershipApplication
from app.models.vehicle import Vehicle, Driver, DriverVehicleAssignment, VehicleMaintenance
from app.models.document import Document, Correspondence, Report, Invoice
from app.models.subscription import Subscription, SubscriptionType
import logging
import sqlite3

def setup_database():
    # Get the absolute path of the project directory
    project_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(project_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Set the database path
    db_path = os.path.join(data_dir, 'app.db')
    print(f"Database will be created at: {db_path}")
    
    # Create an empty database file if it doesn't exist
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.close()
        print(f"Created empty database file at: {db_path}")
    
    app = create_app()
    with app.app_context():
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        try:
            # Drop all tables
            db.drop_all()
            logger.info("Dropped all tables")
            
            # Create all tables
            db.create_all()
            logger.info("Created all tables")
            
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                full_name='System Administrator',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            logger.info("Created admin user")
            
            # Add basic expense types
            expense_types = [
                'مصاريف تشغيلية',
                'مصاريف صيانة',
                'مصاريف رواتب',
                'مصاريف إدارية',
                'مصاريف أخرى'
            ]
            for name in expense_types:
                expense_type = ExpenseType(name=name)
                db.session.add(expense_type)
            db.session.commit()
            logger.info("Added basic expense types")
            
            # Add basic income sources
            income_sources = [
                'رسوم الطلاب',
                'اشتراكات النقل',
                'اشتراكات الأعضاء',
                'تبرعات',
                'إيرادات أخرى'
            ]
            for name in income_sources:
                income_source = IncomeSource(name=name)
                db.session.add(income_source)
            db.session.commit()
            logger.info("Added basic income sources")
            
            # Verify database file exists and has content
            if os.path.exists(db_path) and os.path.getsize(db_path) > 0:
                logger.info(f"Database file created successfully at: {db_path}")
                logger.info(f"Database file size: {os.path.getsize(db_path)} bytes")
            else:
                logger.error(f"Database file was not created or is empty at: {db_path}")
            
            logger.info("Database has been set up successfully!")
            
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print(f"Admin user exists: {admin.username}")
                print(f"Password hash: {admin.password_hash}")
            else:
                print("Admin user not found")
            
        except Exception as e:
            logger.error(f"Error setting up database: {str(e)}")
            raise

if __name__ == '__main__':
    setup_database() 