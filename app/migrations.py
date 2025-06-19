from app import db
from app.models.finance import Income, IncomeSource, Expense, ExpenseType, CashBox, BankAccount, Transfer
from app.models.user import User
from app.models.student import Student, TransportSubscription, EducationalLevel, Program, StudentEnrollment
from app.models.member import Member, MembershipApplication
from app.models.activity import Activity, Meeting, MeetingAttachment
from app.models.document import Document, Correspondence, Report, Invoice
from app.models.vehicle import Vehicle, Driver, VehicleMaintenance
from app.models.subscription import Subscription, SubscriptionType

def init_db():
    # حذف جميع الجداول الموجودة
    db.drop_all()
    
    # إنشاء جميع الجداول
    db.create_all()
    
    # إضافة بعض البيانات الأساسية
    # إضافة مستخدم مسؤول
    admin = User(
        username='admin',
        email='admin@example.com',
        full_name='المدير',
        role='admin'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # إضافة أنواع المصاريف الأساسية
    expense_types = [
        ExpenseType(name='رواتب', description='رواتب الموظفين'),
        ExpenseType(name='إيجار', description='إيجار المقر'),
        ExpenseType(name='كهرباء', description='فواتير الكهرباء'),
        ExpenseType(name='ماء', description='فواتير الماء'),
        ExpenseType(name='صيانة', description='مصاريف الصيانة'),
        ExpenseType(name='أخرى', description='مصاريف متنوعة')
    ]
    db.session.add_all(expense_types)
    
    # إضافة مصادر الدخل الأساسية
    income_sources = [
        IncomeSource(name='اشتراكات', description='اشتراكات الأعضاء'),
        IncomeSource(name='تبرعات', description='تبرعات'),
        IncomeSource(name='أنشطة', description='إيرادات الأنشطة'),
        IncomeSource(name='أخرى', description='إيرادات متنوعة')
    ]
    db.session.add_all(income_sources)
    
    # حفظ التغييرات
    db.session.commit()

if __name__ == '__main__':
    init_db() 