from app import create_app, db
from app.models.finance import CashBox, BankAccount, Transfer, Income, Expense, IncomeSource, ExpenseType
from app.models.user import User
from app.models.student import Student, TransportSubscription, EducationalLevel, Program, StudentEnrollment, PendingStudent

def recreate_tables():
    app = create_app()
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            full_name='System Administrator',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Add basic expense types
        expense_types = [
            ExpenseType(name='رواتب', description='رواتب الموظفين'),
            ExpenseType(name='إيجار', description='إيجار المقر'),
            ExpenseType(name='كهرباء', description='فواتير الكهرباء'),
            ExpenseType(name='ماء', description='فواتير الماء'),
            ExpenseType(name='صيانة', description='مصاريف الصيانة'),
            ExpenseType(name='أخرى', description='مصاريف متنوعة')
        ]
        db.session.add_all(expense_types)
        
        # Add basic income sources
        income_sources = [
            IncomeSource(name='اشتراكات', description='اشتراكات الأعضاء'),
            IncomeSource(name='تبرعات', description='تبرعات'),
            IncomeSource(name='أنشطة', description='إيرادات الأنشطة'),
            IncomeSource(name='أخرى', description='إيرادات متنوعة')
        ]
        db.session.add_all(income_sources)
        
        # Commit all changes
        db.session.commit()
        print("All tables recreated successfully!")

if __name__ == '__main__':
    recreate_tables() 