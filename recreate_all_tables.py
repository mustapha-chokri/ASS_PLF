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

def recreate_all_tables():
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
            
            logger.info("Database has been recreated successfully!")
            
        except Exception as e:
            logger.error(f"Error recreating database: {str(e)}")
            raise

if __name__ == '__main__':
    recreate_all_tables() 