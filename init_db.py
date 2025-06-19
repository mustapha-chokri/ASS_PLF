from app import create_app, db
from app.models.finance import Income, IncomeSource, Expense, ExpenseType, CashBox, BankAccount, Transfer
from app.models.user import User
from app.models.about import About, BoardMember, Mandate
from datetime import datetime

app = create_app()

def init_db():
    with app.app_context():
        # حذف جميع الجداول الموجودة
        db.drop_all()
        
        # إنشاء جميع الجداول
        db.create_all()
        
        # إضافة بعض البيانات الأساسية
        # إضافة مستخدم مسؤول
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                full_name='المدير',
                is_admin=True
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
        
        # إضافة معلومات الجمعية الافتراضية
        about = About.query.first()
        if not about:
            about = About(
                title='جمعية المحبة للتنمية والتعاون',
                content='''
                <h4 class="text-primary mb-3">تعريف الجمعية</h4>
                <p>
                    جمعية المحبة للتنمية والتعاون هي جمعية مغربية تأسست في عام 2015 بهدف تعزيز التنمية المستدامة والتعاون بين أفراد المجتمع. تتخذ الجمعية من قيم التضامن والتعاون والمحبة منهجاً لها في تحقيق أهدافها.
                </p>
                
                <hr class="my-4">
                
                <h4 class="text-primary mb-3">رؤية الجمعية</h4>
                <p>
                    تسعى جمعية المحبة للتنمية والتعاون إلى المساهمة في بناء مجتمع متضامن ومتماسك، يتمتع أفراده بحياة كريمة في إطار التنمية المستدامة، وتطمح الجمعية إلى أن تكون نموذجاً يحتذى به في العمل التطوعي والتضامني على الصعيد المحلي والإقليمي.
                </p>
                
                <hr class="my-4">
                
                <h4 class="text-primary mb-3">رسالة الجمعية</h4>
                <p>
                    تعمل الجمعية على ترسيخ قيم التضامن والتعاون والمحبة بين أفراد المجتمع، والمساهمة في تحقيق التنمية المستدامة، من خلال تنفيذ مشاريع وبرامج تنموية تلبي احتياجات الفئات المستهدفة، وتعزيز الشراكات مع مختلف الفاعلين في المجال التنموي.
                </p>
                
                <hr class="my-4">
                
                <h4 class="text-primary mb-3">أهداف الجمعية</h4>
                <ul class="list-group list-group-flush">
                    <li class="list-group-item">
                        <i class="fas fa-check-circle text-success me-2"></i>
                        المساهمة في تحسين الظروف المعيشية للفئات الهشة والمحتاجة
                    </li>
                    <li class="list-group-item">
                        <i class="fas fa-check-circle text-success me-2"></i>
                        دعم التعليم والتربية لأبناء الأسر المعوزة
                    </li>
                    <li class="list-group-item">
                        <i class="fas fa-check-circle text-success me-2"></i>
                        تنظيم أنشطة ثقافية وتربوية لفائدة الأطفال والشباب
                    </li>
                    <li class="list-group-item">
                        <i class="fas fa-check-circle text-success me-2"></i>
                        تقديم المساعدات الاجتماعية للأرامل واليتامى وذوي الاحتياجات الخاصة
                    </li>
                    <li class="list-group-item">
                        <i class="fas fa-check-circle text-success me-2"></i>
                        المساهمة في حماية البيئة والموارد الطبيعية
                    </li>
                    <li class="list-group-item">
                        <i class="fas fa-check-circle text-success me-2"></i>
                        إقامة شراكات مع الهيئات والمؤسسات الوطنية والدولية
                    </li>
                </ul>
                '''
            )
            db.session.add(about)
        
        # إضافة أعضاء المكتب الافتراضيين
        if not BoardMember.query.first():
            members = [
                BoardMember(
                    name='محمد أمين العلوي',
                    position='الرئيس',
                    description='عضو مؤسس للجمعية ورئيس المكتب منذ سنة 2018. له خبرة واسعة في مجال العمل الجمعوي والتنموي.'
                ),
                BoardMember(
                    name='فاطمة الزهراء مروان',
                    position='نائب الرئيس',
                    description='انضمت للجمعية سنة 2016، ولها إسهامات كبيرة في تطوير البرامج التربوية والتعليمية للجمعية.'
                ),
                BoardMember(
                    name='عبد الرحمان المنصوري',
                    position='الكاتب العام',
                    description='من الأعضاء المؤسسين للجمعية، يتولى مهام الكتابة العامة منذ التأسيس، ويشرف على توثيق أنشطة الجمعية.'
                ),
                BoardMember(
                    name='عمر الحسني',
                    position='أمين المال',
                    description='انضم للجمعية سنة 2017، ويتولى مهام تدبير مالية الجمعية وإعداد التقارير المالية.'
                ),
                BoardMember(
                    name='سلمى الراشدي',
                    position='نائب أمين المال',
                    description='انضمت للجمعية سنة 2019، وتساعد في تدبير مالية الجمعية وتطوير استراتيجيات لتنمية الموارد المالية.'
                ),
                BoardMember(
                    name='يوسف العمراني',
                    position='مستشار',
                    description='عضو مؤسس للجمعية، يقدم استشارات تربوية وإدارية للجمعية ويشرف على برامج التعليم والتكوين.'
                )
            ]
            db.session.add_all(members)
        
        # إضافة فترات الانتداب الافتراضية
        if not Mandate.query.first():
            mandates = [
                Mandate(
                    title='الفترة الثالثة (2021-2024)',
                    start_date=datetime(2021, 1, 15),
                    end_date=datetime(2024, 1, 15),
                    description='تم انتخاب المكتب الحالي خلال الجمع العام العادي المنعقد بتاريخ 15 يناير 2021، وتمتد فترة الانتداب لمدة ثلاث سنوات حسب القانون الأساسي للجمعية.'
                ),
                Mandate(
                    title='الفترة الثانية (2018-2021)',
                    start_date=datetime(2018, 1, 15),
                    end_date=datetime(2021, 1, 15),
                    description='المكتب المسير برئاسة محمد أمين العلوي. أهم الإنجازات: برنامج الدعم المدرسي، حملات طبية، دورات تكوينية'
                ),
                Mandate(
                    title='الفترة الأولى (2015-2018)',
                    start_date=datetime(2015, 1, 15),
                    end_date=datetime(2018, 1, 15),
                    description='المكتب المسير برئاسة أحمد الناصري. أهم الإنجازات: تأسيس الجمعية، بناء مقر الجمعية، إطلاق البرامج الأولى'
                )
            ]
            db.session.add_all(mandates)
        
        # حفظ التغييرات
        db.session.commit()
        print('تم تهيئة قاعدة البيانات بنجاح')

if __name__ == '__main__':
    init_db() 