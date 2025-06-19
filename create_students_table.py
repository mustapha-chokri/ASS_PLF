from app import create_app, db
# استيراد جميع النماذج
from app.models.student import Student, TransportSubscription, EducationalLevel, Program, StudentEnrollment, PendingStudent
from app.models.user import User
from app.models.finance import Income, Expense, ExpenseCategory, Treasury, FinancialReport

app = create_app()

with app.app_context():
    # إنشاء جميع الجداول
    db.create_all()
    print("All tables created successfully!")
    
    # طباعة الجداول الموجودة
    print("\nTables in database:")
    for table in db.metadata.tables:
        print(f"- {table}")

if __name__ == '__main__':
    create_students_table() 