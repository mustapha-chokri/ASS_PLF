from flask import render_template, redirect, url_for, flash, request, jsonify, abort, send_file, current_app
from flask_login import login_required, current_user
from app import db
from app.controllers.students import students_bp
from app.models.student import Student, TransportSubscription, EducationalLevel, PendingStudent
from app.controllers.students.forms import StudentForm, TransportSubscriptionForm, EducationalLevelForm, ImportStudentsForm, ImportTransportSubscriptionsForm, RegistrationLinkForm, StudentRegistrationForm
from datetime import datetime, date, timedelta
import os
from werkzeug.utils import secure_filename
import pandas as pd
import io
import secrets
import string
import calendar
from sqlalchemy import extract, and_, inspect
from wtforms import SelectField, StringField, IntegerField, FloatField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional
from flask_wtf import FlaskForm
import random

# Create pending_students table if it doesn't exist
# Not needed anymore - using SQLAlchemy model instead
# def create_pending_students_table():
#    inspector = inspect(db.engine)
#    if not inspector.has_table('pending_students'):
#        db.session.execute('''
#        CREATE TABLE pending_students (
#            id INTEGER PRIMARY KEY AUTOINCREMENT,
#            registration_token VARCHAR(50) NOT NULL,
#            first_name VARCHAR(100),
#            last_name VARCHAR(100),
#            gender VARCHAR(10),
#            massar_number VARCHAR(100),
#            birth_date DATE,
#            educational_level VARCHAR(100),
#            institution VARCHAR(100),
#            guardian_name VARCHAR(100),
#            guardian_national_id VARCHAR(100),
#            guardian_phone VARCHAR(20),
#            guardian_email VARCHAR(100),
#            address TEXT,
#            student_photo VARCHAR(255),
#            guardian_id_front VARCHAR(255),
#            guardian_id_back VARCHAR(255),
#            commitment_doc VARCHAR(255),
#            notes TEXT,
#            submission_date DATETIME,
#            status VARCHAR(20),
#            admin_notes TEXT
#        )
#        ''')
#        db.session.commit()
#        print("Table 'pending_students' created successfully")

# Call the function to create the table if needed
# Don't call here - this is outside application context
# create_pending_students_table()

# Ensure required directories exist
def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

# Students list
@students_bp.route('/')
@login_required
def index():
    # Get filter parameters
    educational_level = request.args.get('educational_level')
    institution = request.args.get('institution')
    fee_min = request.args.get('fee_min', type=float)
    fee_max = request.args.get('fee_max', type=float)
    status = request.args.get('status')
    
    # Build query with filters
    query = Student.query
    
    if educational_level:
        query = query.filter(Student.educational_level == educational_level)
    
    if institution:
        query = query.filter(Student.institution == institution)
    
    if fee_min is not None:
        query = query.filter(Student.monthly_fee >= fee_min)
    
    if fee_max is not None:
        query = query.filter(Student.monthly_fee <= fee_max)
    
    if status:
        if status == 'blacklisted':
            query = query.filter(Student.is_blacklisted == True)
        else:
            query = query.filter(Student.status == status)
    
    # Get all students with filters applied
    students = query.all()
    
    # Get unique educational levels for filter dropdown
    educational_levels = EducationalLevel.query.order_by(EducationalLevel.order).all()
    
    # Get unique institutions for filter dropdown
    institutions = db.session.query(Student.institution).filter(Student.institution != None, Student.institution != '').distinct().order_by(Student.institution).all()
    institutions = [inst[0] for inst in institutions]
    
    return render_template('students/index.html', 
                         title='قائمة التلاميذ', 
                         students=students, 
                         educational_levels=educational_levels,
                         institutions=institutions)

# Add new student
@students_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = StudentForm()
    
    # Populate educational levels dropdown
    form.educational_level.choices = [(level.name, level.name) for level in 
                                      EducationalLevel.query.order_by(EducationalLevel.order).all()]
    
    if form.validate_on_submit():
        # Check if student ID already exists
        existing_student = Student.query.filter_by(student_id=form.student_id.data).first()
        if existing_student:
            flash('رقم التلميذ موجود بالفعل. الرجاء استخدام رقم آخر.', 'danger')
            return render_template('students/add.html', title='إضافة تلميذ جديد', form=form)
        
        student = Student(
            student_id=form.student_id.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            gender=form.gender.data,
            massar_number=form.massar_number.data,
            birth_date=form.birth_date.data,
            educational_level=form.educational_level.data,
            institution=form.institution.data,
            monthly_fee=form.monthly_fee.data,
            guardian_name=form.guardian_name.data,
            guardian_national_id=form.guardian_national_id.data,
            guardian_phone=form.guardian_phone.data,
            guardian_email=form.guardian_email.data,
            address=form.address.data,
            notes=form.notes.data,
            status=form.status.data,
            registration_date=datetime.now().date()
        )
        
        # Handle file uploads
        if form.student_photo.data:
            upload_dir = os.path.join('app/static/uploads/students/photos')
            ensure_dir(upload_dir + '/')
            # Check if the data is a file object or a string
            if hasattr(form.student_photo.data, 'filename'):
                filename = secure_filename(f"{form.student_id.data}_{form.student_photo.data.filename}")
                photo_path = os.path.join(upload_dir, filename)
                form.student_photo.data.save(photo_path)
                student.student_photo = f"uploads/students/photos/{filename}"
        
        if form.guardian_id_front.data:
            upload_dir = os.path.join('app/static/uploads/students/documents')
            ensure_dir(upload_dir + '/')
            # Check if the data is a file object or a string
            if hasattr(form.guardian_id_front.data, 'filename'):
                filename = secure_filename(f"{form.student_id.data}_id_front_{form.guardian_id_front.data.filename}")
                path = os.path.join(upload_dir, filename)
                form.guardian_id_front.data.save(path)
                student.guardian_id_front = f"uploads/students/documents/{filename}"
        
        if form.guardian_id_back.data:
            upload_dir = os.path.join('app/static/uploads/students/documents')
            ensure_dir(upload_dir + '/')
            # Check if the data is a file object or a string
            if hasattr(form.guardian_id_back.data, 'filename'):
                filename = secure_filename(f"{form.student_id.data}_id_back_{form.guardian_id_back.data.filename}")
                path = os.path.join(upload_dir, filename)
                form.guardian_id_back.data.save(path)
                student.guardian_id_back = f"uploads/students/documents/{filename}"
        
        if form.commitment_doc.data:
            upload_dir = os.path.join('app/static/uploads/students/documents')
            ensure_dir(upload_dir + '/')
            # Check if the data is a file object or a string
            if hasattr(form.commitment_doc.data, 'filename'):
                filename = secure_filename(f"{form.student_id.data}_commitment_{form.commitment_doc.data.filename}")
                path = os.path.join(upload_dir, filename)
                form.commitment_doc.data.save(path)
                student.commitment_doc = f"uploads/students/documents/{filename}"
        
        db.session.add(student)
        db.session.commit()
        flash('تمت إضافة التلميذ بنجاح!', 'success')
        return redirect(url_for('students.index'))
    
    return render_template('students/add.html', title='إضافة تلميذ جديد', form=form)

# View student details
@students_bp.route('/view/<int:id>')
@login_required
def view(id):
    student = Student.query.get_or_404(id)
    subscriptions = TransportSubscription.query.filter_by(student_id=id).order_by(
        TransportSubscription.year.desc(), 
        TransportSubscription.month.desc()
    ).all()
    
    # Convert month numbers to names for display
    month_names = {
        1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
        5: 'ماي', 6: 'يونيو', 7: 'يوليوز', 8: 'غشت',
        9: 'شتنبر', 10: 'أكتوبر', 11: 'نونبر', 12: 'دجنبر'
    }
    
    return render_template(
        'students/view.html', 
        title=f'بيانات التلميذ: {student.full_name}',
        student=student, 
        subscriptions=subscriptions,
        month_names=month_names
    )

# Edit student
@students_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    student = Student.query.get_or_404(id)
    form = StudentForm(obj=student)
    
    # Populate educational levels dropdown
    form.educational_level.choices = [(level.name, level.name) for level in 
                                      EducationalLevel.query.order_by(EducationalLevel.order).all()]
    
    if form.validate_on_submit():
        # Check if student ID already exists and is not this student
        existing_student = Student.query.filter_by(student_id=form.student_id.data).first()
        if existing_student and existing_student.id != student.id:
            flash('رقم التلميذ موجود بالفعل. الرجاء استخدام رقم آخر.', 'danger')
            return render_template('students/edit.html', title='تعديل بيانات تلميذ', form=form, student=student)
        
        student.student_id = form.student_id.data
        student.first_name = form.first_name.data
        student.last_name = form.last_name.data
        student.gender = form.gender.data
        student.massar_number = form.massar_number.data
        student.birth_date = form.birth_date.data
        student.educational_level = form.educational_level.data
        student.institution = form.institution.data
        student.monthly_fee = form.monthly_fee.data
        student.guardian_name = form.guardian_name.data
        student.guardian_national_id = form.guardian_national_id.data
        student.guardian_phone = form.guardian_phone.data
        student.guardian_email = form.guardian_email.data
        student.address = form.address.data
        student.notes = form.notes.data
        student.status = form.status.data
        
        # Handle file uploads
        if form.student_photo.data:
            upload_dir = os.path.join('app/static/uploads/students/photos')
            ensure_dir(upload_dir + '/')
            # Check if the data is a file object or a string
            if hasattr(form.student_photo.data, 'filename'):
                filename = secure_filename(f"{form.student_id.data}_{form.student_photo.data.filename}")
                photo_path = os.path.join(upload_dir, filename)
                form.student_photo.data.save(photo_path)
                student.student_photo = f"uploads/students/photos/{filename}"
        
        if form.guardian_id_front.data:
            upload_dir = os.path.join('app/static/uploads/students/documents')
            ensure_dir(upload_dir + '/')
            # Check if the data is a file object or a string
            if hasattr(form.guardian_id_front.data, 'filename'):
                filename = secure_filename(f"{form.student_id.data}_id_front_{form.guardian_id_front.data.filename}")
                path = os.path.join(upload_dir, filename)
                form.guardian_id_front.data.save(path)
                student.guardian_id_front = f"uploads/students/documents/{filename}"
        
        if form.guardian_id_back.data:
            upload_dir = os.path.join('app/static/uploads/students/documents')
            ensure_dir(upload_dir + '/')
            # Check if the data is a file object or a string
            if hasattr(form.guardian_id_back.data, 'filename'):
                filename = secure_filename(f"{form.student_id.data}_id_back_{form.guardian_id_back.data.filename}")
                path = os.path.join(upload_dir, filename)
                form.guardian_id_back.data.save(path)
                student.guardian_id_back = f"uploads/students/documents/{filename}"
        
        if form.commitment_doc.data:
            upload_dir = os.path.join('app/static/uploads/students/documents')
            ensure_dir(upload_dir + '/')
            # Check if the data is a file object or a string
            if hasattr(form.commitment_doc.data, 'filename'):
                filename = secure_filename(f"{form.student_id.data}_commitment_{form.commitment_doc.data.filename}")
                path = os.path.join(upload_dir, filename)
                form.commitment_doc.data.save(path)
                student.commitment_doc = f"uploads/students/documents/{filename}"
        
        db.session.commit()
        flash('تم تحديث بيانات التلميذ بنجاح!', 'success')
        return redirect(url_for('students.view', id=student.id))
    
    return render_template('students/edit.html', title='تعديل بيانات تلميذ', form=form, student=student)

# Delete student
@students_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    student = Student.query.get_or_404(id)
    
    # Check if there are related subscriptions
    if TransportSubscription.query.filter_by(student_id=id).count() > 0:
        flash('لا يمكن حذف هذا التلميذ لوجود اشتراكات نقل مرتبطة به', 'danger')
        return redirect(url_for('students.view', id=student.id))
    
    # Remove files if they exist
    for attr in ['student_photo', 'guardian_id_front', 'guardian_id_back', 'commitment_doc']:
        if getattr(student, attr):
            try:
                file_path = os.path.join('app/static', getattr(student, attr))
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
    
    db.session.delete(student)
    db.session.commit()
    flash('تم حذف التلميذ بنجاح', 'success')
    return redirect(url_for('students.index'))

# Transport subscriptions management
@students_bp.route('/transport-subscriptions')
@login_required
def transport_subscriptions():
    # Get filter parameters from request
    search_query = request.args.get('search', '')
    month_filter = request.args.get('month', type=int)
    year_filter = request.args.get('year', type=int)
    level_filter = request.args.get('level')
    payment_method_filter = request.args.get('payment_method')
    
    # Current month and year for stats cards
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Build query with filters
    query = TransportSubscription.query.join(Student, TransportSubscription.student_id == Student.id)
    
    # Apply filters if provided
    if search_query:
        query = query.filter(
            db.or_(
                Student.student_id.like(f'%{search_query}%'),
                Student.first_name.like(f'%{search_query}%'),
                Student.last_name.like(f'%{search_query}%')
            )
        )
    
    if month_filter:
        query = query.filter(TransportSubscription.month == month_filter)
    
    if year_filter:
        query = query.filter(TransportSubscription.year == year_filter)
    
    if level_filter:
        query = query.filter(Student.educational_level == level_filter)
    
    if payment_method_filter:
        query = query.filter(TransportSubscription.payment_method == payment_method_filter)
    
    # Get filtered subscriptions
    subscriptions = query.order_by(
        TransportSubscription.year.desc(),
        TransportSubscription.month.desc()
    ).all()
    
    # Calculate filtered total amount
    filtered_amount = sum(subscription.amount for subscription in subscriptions)
    
    # Monthly subscriptions for stats card (current month/year)
    monthly_subscriptions = TransportSubscription.query.filter(
        TransportSubscription.month == current_month,
        TransportSubscription.year == current_year
    ).count()
    
    # Monthly amount for stats card (current month/year)
    monthly_amount = db.session.query(db.func.sum(TransportSubscription.amount)).filter(
        TransportSubscription.month == current_month,
        TransportSubscription.year == current_year
    ).scalar() or 0
    
    # Month names in Arabic
    month_names = {
        1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
        5: 'ماي', 6: 'يونيو', 7: 'يوليوز', 8: 'غشت',
        9: 'شتنبر', 10: 'أكتوبر', 11: 'نونبر', 12: 'دجنبر'
    }
    
    # Get educational levels for filter dropdown
    educational_levels = [level.name for level in EducationalLevel.query.order_by(EducationalLevel.order).all()]
    
    # Get years for filter dropdown (current year and 2 years before/after)
    years = list(range(current_year - 2, current_year + 3))
    
    return render_template(
        'students/transport_subscriptions.html',
        title='اشتراكات النقل المدرسي',
        subscriptions=subscriptions,
        monthly_subscriptions=monthly_subscriptions,
        monthly_amount=monthly_amount,
        filtered_amount=filtered_amount,
        current_month=month_names[current_month],
        current_year=current_year,
        month_names=month_names,
        search_query=search_query,
        month_filter=month_filter,
        year_filter=year_filter,
        level_filter=level_filter,
        payment_method_filter=payment_method_filter,
        educational_levels=educational_levels,
        years=years,
        filtered_count=len(subscriptions)
    )

# Add transport subscription
@students_bp.route('/transport-subscriptions/add', methods=['GET', 'POST'])
@login_required
def add_transport_subscription():
    # Create form
    form = TransportSubscriptionForm()
    
    # Populate the student choices
    form.student_id.choices = [(s.id, f"{s.student_id} - {s.full_name}") 
                              for s in Student.query.filter_by(status='active').order_by(Student.first_name).all()]
    
    # Populate year choices
    current_year = datetime.now().year
    form.year.choices = [(y, str(y)) for y in range(current_year - 2, current_year + 3)]
    
    if form.validate_on_submit():
        # Check if subscription already exists for this month/year
        existing_sub = TransportSubscription.query.filter_by(
            student_id=form.student_id.data,
            month=form.month.data,
            year=form.year.data
        ).first()
        
        if existing_sub:
            flash('يوجد بالفعل اشتراك لهذا التلميذ في هذا الشهر/السنة!', 'danger')
            return render_template('students/add_transport_subscription.html', title='إضافة اشتراك نقل جديد', form=form)
        
        subscription = TransportSubscription(
            student_id=form.student_id.data,
            month=form.month.data,
            year=form.year.data,
            amount=form.amount.data,
            payment_date=form.payment_date.data,
            payment_method=form.payment_method.data,
            receipt_number=form.receipt_number.data,
            notes=form.notes.data,
            created_by=current_user.id
        )
        
        db.session.add(subscription)
        db.session.commit()
        flash('تم تسجيل اشتراك النقل بنجاح!', 'success')
        return redirect(url_for('students.transport_subscriptions'))
    
    # Pre-fill the current month and year
    if not form.month.data:
        form.month.data = datetime.now().month
    if not form.year.data:
        form.year.data = datetime.now().year
    
    return render_template('students/add_transport_subscription.html', title='إضافة اشتراك نقل جديد', form=form)

# Add transport subscription for a specific student
@students_bp.route('/transport-subscriptions/add/<int:student_id>', methods=['GET', 'POST'])
@login_required
def add_student_transport_subscription(student_id):
    student = Student.query.get_or_404(student_id)
    form = TransportSubscriptionForm()
    
    # Populate the student choices
    form.student_id.choices = [(s.id, f"{s.student_id} - {s.full_name}") 
                              for s in Student.query.filter_by(status='active').order_by(Student.first_name).all()]
    
    # Populate year choices
    current_year = datetime.now().year
    form.year.choices = [(y, str(y)) for y in range(current_year - 2, current_year + 3)]
    
    if form.validate_on_submit():
        # Check if subscription already exists for this month/year
        existing_sub = TransportSubscription.query.filter_by(
            student_id=student.id,
            month=form.month.data,
            year=form.year.data
        ).first()
        
        if existing_sub:
            flash('يوجد بالفعل اشتراك لهذا التلميذ في هذا الشهر/السنة!', 'danger')
            return render_template('students/add_transport_subscription.html', 
                                title='إضافة اشتراك نقل', 
                                form=form, 
                                student=student)
        
        # Use student's monthly fee if amount is not specified
        amount = form.amount.data or student.monthly_fee
        
        subscription = TransportSubscription(
            student_id=student.id,
            month=form.month.data,
            year=form.year.data,
            amount=amount,
            payment_date=form.payment_date.data,
            payment_method=form.payment_method.data,
            receipt_number=form.receipt_number.data,
            notes=form.notes.data,
            created_by=current_user.id
        )
        
        db.session.add(subscription)
        db.session.commit()
        flash('تم تسجيل اشتراك النقل بنجاح!', 'success')
        return redirect(url_for('students.view', id=student.id))
    
    # Pre-fill the current month and year and student's monthly fee
    if not form.month.data:
        form.month.data = datetime.now().month
    if not form.year.data:
        form.year.data = datetime.now().year
    if not form.amount.data:
        form.amount.data = student.monthly_fee
    
    return render_template('students/add_transport_subscription.html', 
                          title='إضافة اشتراك نقل', 
                          form=form, 
                          student=student)

# Edit transport subscription
@students_bp.route('/transport-subscription/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_transport_subscription(id):
    subscription = TransportSubscription.query.get_or_404(id)
    form = TransportSubscriptionForm(obj=subscription)
    
    # Populate the student choices
    form.student_id.choices = [(s.id, f"{s.student_id} - {s.full_name}") 
                              for s in Student.query.filter_by(status='active').order_by(Student.first_name).all()]
    
    # Populate year choices
    current_year = datetime.now().year
    form.year.choices = [(y, str(y)) for y in range(current_year - 2, current_year + 3)]
    
    if form.validate_on_submit():
        # Check if new month/year combo already exists for this student (excluding this subscription)
        if subscription.month != form.month.data or subscription.year != form.year.data:
            existing_sub = TransportSubscription.query.filter(
                TransportSubscription.student_id == subscription.student_id,
                TransportSubscription.month == form.month.data,
                TransportSubscription.year == form.year.data,
                TransportSubscription.id != subscription.id
            ).first()
            
            if existing_sub:
                flash('يوجد بالفعل اشتراك لهذا التلميذ في هذا الشهر/السنة!', 'danger')
                return render_template('students/edit_transport_subscription.html', 
                                    title='تعديل اشتراك النقل', 
                                    form=form, 
                                    subscription=subscription)
        
        subscription.month = form.month.data
        subscription.year = form.year.data
        subscription.amount = form.amount.data
        subscription.payment_date = form.payment_date.data
        subscription.payment_method = form.payment_method.data
        subscription.receipt_number = form.receipt_number.data
        subscription.notes = form.notes.data
        
        db.session.commit()
        flash('تم تعديل اشتراك النقل بنجاح!', 'success')
        return redirect(url_for('students.view', id=subscription.student_id))
    
    return render_template('students/edit_transport_subscription.html', 
                          title='تعديل اشتراك النقل', 
                          form=form, 
                          subscription=subscription,
                          student=subscription.student)

# Delete transport subscription
@students_bp.route('/transport-subscription/delete/<int:id>', methods=['POST'])
@login_required
def delete_transport_subscription(id):
    subscription = TransportSubscription.query.get_or_404(id)
    student_id = subscription.student_id
    
    db.session.delete(subscription)
    db.session.commit()
    
    flash('تم حذف اشتراك النقل بنجاح!', 'success')
    return redirect(url_for('students.view', id=student_id))

# Print transport subscription receipt
@students_bp.route('/transport-subscription/receipt/<int:id>')
@login_required
def print_receipt(id):
    subscription = TransportSubscription.query.get_or_404(id)
    
    # Get month name in Arabic
    month_names = {
        1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
        5: 'ماي', 6: 'يونيو', 7: 'يوليوز', 8: 'غشت',
        9: 'شتنبر', 10: 'أكتوبر', 11: 'نونبر', 12: 'دجنبر'
    }
    
    month_name = month_names.get(subscription.month, '')
    
    return render_template('students/print_receipt.html', 
                          title='طباعة إيصال النقل المدرسي', 
                          subscription=subscription,
                          month_name=month_name)

# Educational levels management
@students_bp.route('/educational-levels')
@login_required
def educational_levels():
    levels = EducationalLevel.query.order_by(EducationalLevel.order).all()
    
    # Get student count for each level
    for level in levels:
        level.students_count = Student.query.filter_by(educational_level=level.name).count()
    
    return render_template('students/educational_levels.html', 
                          title='المستويات الدراسية',
                          levels=levels,
                          form=EducationalLevelForm(),
                          edit_form=EducationalLevelForm())

# Add educational level
@students_bp.route('/educational-levels/add', methods=['GET', 'POST'])
@login_required
def add_educational_level():
    form = EducationalLevelForm()
    
    if form.validate_on_submit():
        # Check if level already exists
        existing_level = EducationalLevel.query.filter_by(name=form.name.data).first()
        if existing_level:
            flash('هذا المستوى موجود بالفعل!', 'danger')
            return redirect(url_for('students.educational_levels'))
        
        level = EducationalLevel(
            name=form.name.data,
            order=int(form.order.data),
            description=form.description.data
        )
        
        db.session.add(level)
        db.session.commit()
        flash('تمت إضافة المستوى الدراسي بنجاح!', 'success')
        return redirect(url_for('students.educational_levels'))
    
    # If form validation failed, show errors on the educational_levels page
    if form.errors:
        flash_errors(form)
        return redirect(url_for('students.educational_levels'))
    
    return redirect(url_for('students.educational_levels'))

# Edit educational level
@students_bp.route('/educational-levels/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_educational_level(id):
    level = EducationalLevel.query.get_or_404(id)
    form = EducationalLevelForm(obj=level)
    
    if form.validate_on_submit():
        # Check if level already exists (excluding this one)
        existing_level = EducationalLevel.query.filter(
            EducationalLevel.name == form.name.data,
            EducationalLevel.id != level.id
        ).first()
        
        if existing_level:
            flash('هذا المستوى موجود بالفعل!', 'danger')
            return redirect(url_for('students.educational_levels'))
        
        level.name = form.name.data
        level.order = int(form.order.data)
        level.description = form.description.data
        
        db.session.commit()
        flash('تم تعديل المستوى الدراسي بنجاح!', 'success')
        return redirect(url_for('students.educational_levels'))
    
    # If form validation failed, show errors
    if form.errors:
        flash_errors(form)
    
    return redirect(url_for('students.educational_levels'))

# Helper function to display form errors
def flash_errors(form):
    for field, errors in form.errors.items():
        field_name = getattr(form, field).label.text
        for error in errors:
            flash(f'خطأ في حقل "{field_name}": {error}', 'danger')

# Delete educational level
@students_bp.route('/educational-levels/delete/<int:id>', methods=['POST'])
@login_required
def delete_educational_level(id):
    level = EducationalLevel.query.get_or_404(id)
    
    # Check if any students are using this level
    students_using_level = Student.query.filter_by(educational_level=level.name).count()
    if students_using_level > 0:
        flash(f'لا يمكن حذف هذا المستوى لأنه مستخدم من قبل {students_using_level} تلميذ(ة)!', 'danger')
        return redirect(url_for('students.educational_levels'))
    
    db.session.delete(level)
    db.session.commit()
    flash('تم حذف المستوى الدراسي بنجاح!', 'success')
    return redirect(url_for('students.educational_levels'))

# Export students to Excel
@students_bp.route('/export-excel')
@login_required
def export_excel():
    students = Student.query.all()
    
    # Create a DataFrame
    data = {
        'رقم التلميذ': [s.student_id for s in students],
        'الاسم الشخصي': [s.first_name for s in students],
        'النسب': [s.last_name for s in students],
        'رقم مسار': [s.massar_number for s in students],
        'تاريخ الازدياد': [s.birth_date for s in students],
        'المستوى الدراسي': [s.educational_level for s in students],
        'المؤسسة': [s.institution for s in students],
        'مبلغ الاشتراك الشهري': [s.monthly_fee for s in students],
        'اسم ولي الأمر': [s.guardian_name for s in students],
        'رقم البطاقة الوطنية لولي الأمر': [s.guardian_national_id for s in students],
        'رقم هاتف ولي الأمر': [s.guardian_phone for s in students],
        'البريد الإلكتروني لولي الأمر': [s.guardian_email for s in students],
        'العنوان': [s.address for s in students],
        'تاريخ التسجيل': [s.registration_date for s in students],
        'الحالة': [s.status for s in students],
        'ملاحظات': [s.notes for s in students]
    }
    
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='التلاميذ', index=False)
    
    output.seek(0)
    
    # Create a response to download the file
    return send_file(
        output,
        as_attachment=True,
        download_name=f"students_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# Export transport subscriptions to Excel
@students_bp.route('/export-subscriptions-excel')
@login_required
def export_subscriptions_excel():
    subscriptions = TransportSubscription.query.join(
        Student, TransportSubscription.student_id == Student.id
    ).order_by(
        TransportSubscription.year.desc(),
        TransportSubscription.month.desc()
    ).all()
    
    # Month names in Arabic
    month_names = {
        1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
        5: 'ماي', 6: 'يونيو', 7: 'يوليوز', 8: 'غشت',
        9: 'شتنبر', 10: 'أكتوبر', 11: 'نونبر', 12: 'دجنبر'
    }
    
    # Create a DataFrame
    data = {
        'رقم التلميذ': [s.student.student_id for s in subscriptions],
        'الاسم الكامل': [s.student.full_name for s in subscriptions],
        'المستوى الدراسي': [s.student.educational_level for s in subscriptions],
        'الشهر': [month_names.get(s.month) for s in subscriptions],
        'السنة': [s.year for s in subscriptions],
        'المبلغ': [s.amount for s in subscriptions],
        'تاريخ الدفع': [s.payment_date for s in subscriptions],
        'طريقة الدفع': [s.payment_method for s in subscriptions],
        'رقم الإيصال': [s.receipt_number for s in subscriptions],
        'ملاحظات': [s.notes for s in subscriptions]
    }
    
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='اشتراكات النقل', index=False)
    
    output.seek(0)
    
    # Create a response to download the file
    return send_file(
        output,
        as_attachment=True,
        download_name=f"transport_subscriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# Search students
@students_bp.route('/search')
@login_required
def search():
    query = request.args.get('query', '')
    if not query:
        return redirect(url_for('students.index'))
    
    # Search by student_id, first_name, or last_name
    students = Student.query.filter(
        db.or_(
            Student.student_id.like(f'%{query}%'),
            Student.first_name.like(f'%{query}%'),
            Student.last_name.like(f'%{query}%'),
            Student.massar_number.like(f'%{query}%')
        )
    ).all()
    
    return render_template('students/index.html', 
                         title=f'نتائج البحث: {query}',
                         students=students,
                         search_query=query)

# Dashboard API for student statistics
@students_bp.route('/api/stats')
@login_required
def api_stats():
    # Total students
    total_students = Student.query.count()
    active_students = Student.query.filter_by(status='active').count()
    
    # Current month transport subscriptions
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    monthly_subscriptions = TransportSubscription.query.filter(
        TransportSubscription.month == current_month,
        TransportSubscription.year == current_year
    ).count()
    
    monthly_amount = db.session.query(db.func.sum(TransportSubscription.amount)).filter(
        TransportSubscription.month == current_month,
        TransportSubscription.year == current_year
    ).scalar() or 0
    
    # Students with expiring subscriptions (not paid for current month)
    active_students_ids = [s.id for s in Student.query.filter_by(status='active').all()]
    
    subscribed_students_ids = [
        s.student_id for s in TransportSubscription.query.filter(
            TransportSubscription.month == current_month,
            TransportSubscription.year == current_year
        ).all()
    ]
    
    expiring_subscriptions = len([s_id for s_id in active_students_ids if s_id not in subscribed_students_ids])
    
    # Month name in Arabic
    month_names = {
        1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
        5: 'ماي', 6: 'يونيو', 7: 'يوليوز', 8: 'غشت',
        9: 'شتنبر', 10: 'أكتوبر', 11: 'نونبر', 12: 'دجنبر'
    }
    
    current_month_name = month_names.get(current_month)
    
    return jsonify({
        'total_students': total_students,
        'active_students': active_students,
        'monthly_subscriptions': monthly_subscriptions,
        'monthly_amount': monthly_amount,
        'expiring_subscriptions': expiring_subscriptions,
        'current_month': current_month_name,
        'current_year': current_year
    })

# Import students from Excel file
@students_bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_students():
    form = ImportStudentsForm()
    
    if form.validate_on_submit():
        excel_file = form.excel_file.data
        
        # Create a DataFrame from the Excel file
        try:
            df = pd.read_excel(excel_file)
            
            # Required columns in the Excel file
            required_columns = ['رقم التلميذ', 'الاسم الشخصي', 'النسب', 'الجنس', 'المستوى الدراسي', 'مبلغ الاشتراك الشهري']
            
            # Check if all required columns exist in the file
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                flash(f'الملف لا يحتوي على الأعمدة المطلوبة: {", ".join(missing_columns)}', 'danger')
                return render_template('students/import.html', title='استيراد التلاميذ من اكسيل', form=form)
            
            # Process each row
            imported_count = 0
            errors = []
            
            for index, row in df.iterrows():
                student_id = str(row['رقم التلميذ']).strip()
                
                # Skip rows with empty student_id
                if not student_id or pd.isna(student_id):
                    errors.append(f'الصف {index+2}: رقم التلميذ فارغ')
                    continue
                
                # Check if student already exists
                existing_student = Student.query.filter_by(student_id=student_id).first()
                if existing_student:
                    errors.append(f'الصف {index+2}: رقم التلميذ {student_id} موجود بالفعل')
                    continue
                
                # Check for Massar number duplicates if not empty
                massar_number = str(row.get('رقم مسار', '')).strip()
                if massar_number and not pd.isna(massar_number):
                    existing_massar = Student.query.filter_by(massar_number=massar_number).first()
                    if existing_massar:
                        errors.append(f'الصف {index+2}: رقم مسار {massar_number} موجود بالفعل للتلميذ {existing_massar.full_name}')
                        continue
                
                # Extract values
                gender_value = str(row.get('الجنس', '')).strip().lower()
                gender = 'male' if gender_value in ['ذكر', 'male', 'm'] else 'female' if gender_value in ['أنثى', 'female', 'f'] else None
                
                # Process birth date if exists
                birth_date = None
                birth_date_col = row.get('تاريخ الازدياد')
                if birth_date_col and not pd.isna(birth_date_col):
                    try:
                        birth_date = pd.to_datetime(birth_date_col).date()
                    except:
                        errors.append(f'الصف {index+2}: تنسيق تاريخ الازدياد غير صحيح')
                
                # Create new student
                student = Student(
                    student_id=student_id,
                    first_name=str(row['الاسم الشخصي']).strip(),
                    last_name=str(row['النسب']).strip(),
                    gender=gender,
                    massar_number=massar_number if massar_number else None,
                    birth_date=birth_date,
                    educational_level=str(row['المستوى الدراسي']).strip(),
                    institution=str(row.get('المؤسسة', '')).strip() if not pd.isna(row.get('المؤسسة', '')) else None,
                    monthly_fee=float(row['مبلغ الاشتراك الشهري']),
                    guardian_name=str(row.get('اسم ولي الأمر', '')).strip() if not pd.isna(row.get('اسم ولي الأمر', '')) else None,
                    guardian_national_id=str(row.get('رقم البطاقة الوطنية لولي الأمر', '')).strip() if not pd.isna(row.get('رقم البطاقة الوطنية لولي الأمر', '')) else None,
                    guardian_phone=str(row.get('رقم هاتف ولي الأمر', '')).strip() if not pd.isna(row.get('رقم هاتف ولي الأمر', '')) else None,
                    guardian_email=str(row.get('البريد الإلكتروني لولي الأمر', '')).strip() if not pd.isna(row.get('البريد الإلكتروني لولي الأمر', '')) else None,
                    address=str(row.get('العنوان', '')).strip() if not pd.isna(row.get('العنوان', '')) else None,
                    notes=str(row.get('ملاحظات', '')).strip() if not pd.isna(row.get('ملاحظات', '')) else None,
                    status='active',
                    registration_date=datetime.now().date()
                )
                
                db.session.add(student)
                imported_count += 1
            
            db.session.commit()
            
            if imported_count > 0:
                flash(f'تم استيراد {imported_count} تلميذ بنجاح', 'success')
            
            if errors:
                error_message = "<br>".join(errors)
                flash(f'تم العثور على بعض الأخطاء أثناء الاستيراد:<br>{error_message}', 'warning')
            
            return redirect(url_for('students.index'))
            
        except Exception as e:
            flash(f'حدث خطأ أثناء استيراد الملف: {str(e)}', 'danger')
            return render_template('students/import.html', title='استيراد التلاميذ من اكسيل', form=form)
    
    return render_template('students/import.html', title='استيراد التلاميذ من اكسيل', form=form)

# Download Excel template for student import
@students_bp.route('/download-template')
@login_required
def download_template():
    # Create a DataFrame with the required columns
    df = pd.DataFrame(columns=[
        'رقم التلميذ',
        'الاسم الشخصي',
        'النسب',
        'الجنس',  # ذكر أو أنثى
        'رقم مسار',
        'تاريخ الازدياد',  # YYYY-MM-DD
        'المستوى الدراسي',
        'المؤسسة',
        'مبلغ الاشتراك الشهري',
        'اسم ولي الأمر',
        'رقم البطاقة الوطنية لولي الأمر',
        'رقم هاتف ولي الأمر',
        'البريد الإلكتروني لولي الأمر',
        'العنوان',
        'ملاحظات'
    ])
    
    # Add a sample row
    df.loc[0] = [
        'S001',  # رقم التلميذ
        'محمد',  # الاسم الشخصي
        'العلوي',  # النسب
        'ذكر',  # الجنس
        'M123456',  # رقم مسار
        '2010-01-01',  # تاريخ الازدياد
        'المستوى الثالث',  # المستوى الدراسي
        'مدرسة الأمل',  # المؤسسة
        250.0,  # مبلغ الاشتراك الشهري
        'أحمد العلوي',  # اسم ولي الأمر
        'AB123456',  # رقم البطاقة الوطنية لولي الأمر
        '0612345678',  # رقم هاتف ولي الأمر
        'ahmed@example.com',  # البريد الإلكتروني لولي الأمر
        'شارع الحسن الثاني, الرباط',  # العنوان
        'مثال توضيحي'  # ملاحظات
    ]
    
    # Get educational levels from the database
    levels = EducationalLevel.query.order_by(EducationalLevel.order).all()
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='نموذج التلاميذ', index=False)
        
        # Get access to the workbook and the worksheet
        workbook = writer.book
        worksheet = writer.sheets['نموذج التلاميذ']
        
        # Add a new worksheet for instructions
        instructions_sheet = workbook.add_worksheet('تعليمات')
        
        # Format for headers
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D7E4BC',
            'border': 1
        })
        
        # Write instructions
        instructions = [
            ['تعليمات استيراد التلاميذ'],
            [''],
            ['الحقول الإلزامية:'],
            ['رقم التلميذ - يجب أن يكون فريداً'],
            ['الاسم الشخصي'],
            ['النسب'],
            ['الجنس - ذكر أو أنثى'],
            ['المستوى الدراسي - يجب أن يكون من القائمة المعتمدة'],
            ['مبلغ الاشتراك الشهري'],
            [''],
            ['الحقول الاختيارية:'],
            ['رقم مسار - يجب أن يكون فريداً إذا تم تعبئته'],
            ['تاريخ الازدياد - يجب أن يكون بتنسيق YYYY-MM-DD'],
            ['المؤسسة'],
            ['اسم ولي الأمر'],
            ['رقم البطاقة الوطنية لولي الأمر'],
            ['رقم هاتف ولي الأمر'],
            ['البريد الإلكتروني لولي الأمر'],
            ['العنوان'],
            ['ملاحظات'],
            [''],
            ['المستويات الدراسية المعتمدة:']
        ]
        
        # Add educational levels to instructions
        for level in levels:
            instructions.append([level.name])
        
        # Write instructions to the worksheet
        for row_num, instruction in enumerate(instructions):
            instructions_sheet.write(row_num, 0, instruction[0])
        
        # Set column widths
        for col_num, column in enumerate(df.columns):
            column_width = max(15, len(column) + 2)
            worksheet.set_column(col_num, col_num, column_width)
        
        # Format headers
        for col_num, column in enumerate(df.columns):
            worksheet.write(0, col_num, column, header_format)
        
        # Add data validation for gender
        gender_validation = {
            'validate': 'list',
            'source': ['ذكر', 'أنثى']
        }
        worksheet.data_validation(1, 3, 1000, 3, gender_validation)
        
        # Add data validation for educational level
        level_list = [level.name for level in levels]
        level_validation = {
            'validate': 'list',
            'source': level_list
        }
        worksheet.data_validation(1, 6, 1000, 6, level_validation)
    
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=f"students_import_template.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# Import transport subscriptions from Excel file
@students_bp.route('/transport-subscriptions/import', methods=['GET', 'POST'])
@login_required
def import_transport_subscriptions():
    form = ImportTransportSubscriptionsForm()
    
    if form.validate_on_submit():
        excel_file = form.excel_file.data
        
        # Create a DataFrame from the Excel file
        try:
            df = pd.read_excel(excel_file)
            
            # Required columns in the Excel file
            required_columns = ['رقم التلميذ', 'الشهر', 'السنة', 'المبلغ', 'تاريخ الدفع', 'طريقة الدفع']
            
            # Check if all required columns exist in the file
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                flash(f'الملف لا يحتوي على الأعمدة المطلوبة: {", ".join(missing_columns)}', 'danger')
                return render_template('students/import_transport_subscriptions.html', title='استيراد اشتراكات النقل من اكسيل', form=form)
            
            # Process each row
            imported_count = 0
            errors = []
            
            for index, row in df.iterrows():
                student_id = str(row['رقم التلميذ']).strip()
                
                # Skip rows with empty student_id
                if not student_id or pd.isna(student_id):
                    errors.append(f'الصف {index+2}: رقم التلميذ فارغ')
                    continue
                
                # Find the student by student_id
                student = Student.query.filter_by(student_id=student_id).first()
                if not student:
                    errors.append(f'الصف {index+2}: رقم التلميذ {student_id} غير موجود')
                    continue
                
                # Parse month and year
                month_value = row['الشهر']
                year_value = row['السنة']
                
                # Check if month is valid
                if pd.isna(month_value) or month_value < 1 or month_value > 12:
                    errors.append(f'الصف {index+2}: الشهر غير صالح، يجب أن يكون بين 1 و 12')
                    continue
                
                # Check if year is valid
                current_year = datetime.now().year
                if pd.isna(year_value) or year_value < current_year - 5 or year_value > current_year + 5:
                    errors.append(f'الصف {index+2}: السنة غير صالحة')
                    continue
                
                # Convert month to integer
                month = int(month_value)
                year = int(year_value)
                
                # Check if subscription already exists for this month/year
                existing_sub = TransportSubscription.query.filter_by(
                    student_id=student.id,
                    month=month,
                    year=year
                ).first()
                
                if existing_sub:
                    errors.append(f'الصف {index+2}: يوجد بالفعل اشتراك للتلميذ {student_id} في شهر {month}/{year}')
                    continue
                
                # Process payment date
                payment_date = None
                payment_date_col = row.get('تاريخ الدفع')
                if payment_date_col and not pd.isna(payment_date_col):
                    try:
                        payment_date = pd.to_datetime(payment_date_col).date()
                    except:
                        payment_date = datetime.now().date()
                        errors.append(f'الصف {index+2}: تنسيق تاريخ الدفع غير صحيح، تم استخدام التاريخ الحالي')
                else:
                    payment_date = datetime.now().date()
                
                # Process payment method
                payment_method = "cash"  # Default
                payment_method_col = row.get('طريقة الدفع', '').lower().strip() if not pd.isna(row.get('طريقة الدفع', '')) else ''
                
                if payment_method_col in ['نقداً', 'نقدا', 'cash']:
                    payment_method = 'cash'
                elif payment_method_col in ['تحويل بنكي', 'تحويل', 'bank', 'bank_transfer']:
                    payment_method = 'bank_transfer'
                elif payment_method_col in ['شيك', 'check']:
                    payment_method = 'check'
                
                # Create subscription
                amount = float(row['المبلغ']) if not pd.isna(row['المبلغ']) else student.monthly_fee
                receipt_number = str(row.get('رقم الإيصال', '')).strip() if not pd.isna(row.get('رقم الإيصال', '')) else ''
                notes = str(row.get('ملاحظات', '')).strip() if not pd.isna(row.get('ملاحظات', '')) else ''
                
                subscription = TransportSubscription(
                    student_id=student.id,
                    month=month,
                    year=year,
                    amount=amount,
                    payment_date=payment_date,
                    payment_method=payment_method,
                    receipt_number=receipt_number,
                    notes=notes,
                    created_by=current_user.id
                )
                
                db.session.add(subscription)
                imported_count += 1
            
            db.session.commit()
            
            if imported_count > 0:
                flash(f'تم استيراد {imported_count} اشتراك بنجاح', 'success')
            
            if errors:
                error_message = "<br>".join(errors)
                flash(f'تم العثور على بعض الأخطاء أثناء الاستيراد:<br>{error_message}', 'warning')
            
            return redirect(url_for('students.transport_subscriptions'))
            
        except Exception as e:
            flash(f'حدث خطأ أثناء استيراد الملف: {str(e)}', 'danger')
            return render_template('students/import_transport_subscriptions.html', title='استيراد اشتراكات النقل من اكسيل', form=form)
    
    return render_template('students/import_transport_subscriptions.html', title='استيراد اشتراكات النقل من اكسيل', form=form)

# Download Excel template for transport subscription import
@students_bp.route('/transport-subscriptions/download-template')
@login_required
def download_transport_subscriptions_template():
    # Create a DataFrame with the required columns
    df = pd.DataFrame(columns=[
        'رقم التلميذ',
        'الشهر',
        'السنة',
        'المبلغ',
        'تاريخ الدفع',
        'طريقة الدفع',
        'رقم الإيصال',
        'ملاحظات'
    ])
    
    # Add sample rows
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Get some student IDs for the example
    students = Student.query.filter_by(status='active').limit(2).all()
    
    if students:
        # Add a sample row for the first student
        df.loc[0] = [
            students[0].student_id,  # رقم التلميذ
            current_month,  # الشهر
            current_year,  # السنة
            students[0].monthly_fee,  # المبلغ
            datetime.now().date().strftime('%Y-%m-%d'),  # تاريخ الدفع
            'نقداً',  # طريقة الدفع
            'REC-001',  # رقم الإيصال
            'مثال توضيحي 1'  # ملاحظات
        ]
        
        # If there's a second student, add another sample row
        if len(students) > 1:
            df.loc[1] = [
                students[1].student_id,  # رقم التلميذ
                current_month,  # الشهر
                current_year,  # السنة
                students[1].monthly_fee,  # المبلغ
                datetime.now().date().strftime('%Y-%m-%d'),  # تاريخ الدفع
                'تحويل بنكي',  # طريقة الدفع
                'REC-002',  # رقم الإيصال
                'مثال توضيحي 2'  # ملاحظات
            ]
    else:
        # Add a generic sample row if no students are available
        df.loc[0] = [
            'S001',  # رقم التلميذ
            current_month,  # الشهر
            current_year,  # السنة
            250.0,  # المبلغ
            datetime.now().date().strftime('%Y-%m-%d'),  # تاريخ الدفع
            'نقداً',  # طريقة الدفع
            'REC-001',  # رقم الإيصال
            'مثال توضيحي'  # ملاحظات
        ]
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='نموذج اشتراكات النقل', index=False)
        
        # Get access to the workbook and the worksheet
        workbook = writer.book
        worksheet = writer.sheets['نموذج اشتراكات النقل']
        
        # Add a new worksheet for instructions
        instructions_sheet = workbook.add_worksheet('تعليمات')
        
        # Format for headers
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D7E4BC',
            'border': 1
        })
        
        # Write instructions
        instructions = [
            ['تعليمات استيراد اشتراكات النقل'],
            [''],
            ['الحقول الإلزامية:'],
            ['رقم التلميذ - يجب أن يكون موجود في النظام'],
            ['الشهر - يجب أن يكون رقما بين 1 و12'],
            ['السنة - يجب أن تكون السنة الحالية أو السنوات المجاورة'],
            ['المبلغ - قيمة اشتراك النقل بالدرهم'],
            ['تاريخ الدفع - يجب أن يكون بتنسيق YYYY-MM-DD'],
            ['طريقة الدفع - يمكن استخدام: "نقداً"، "تحويل بنكي"، "شيك"'],
            [''],
            ['الحقول الاختيارية:'],
            ['رقم الإيصال - رقم إيصال الدفع إن وجد'],
            ['ملاحظات - أي ملاحظات إضافية'],
            [''],
            ['تنبيه:'],
            ['- لن يتم استيراد الاشتراكات المكررة للطالب نفسه في الشهر والسنة نفسها'],
            ['- في حال وجود أي خطأ في الملف سيتم عرض تفاصيل الأخطاء بعد الاستيراد']
        ]
        
        # Write instructions to the worksheet
        for row_num, instruction in enumerate(instructions):
            instructions_sheet.write(row_num, 0, instruction[0])
        
        # Set column widths
        for col_num, column in enumerate(df.columns):
            column_width = max(15, len(column) + 2)
            worksheet.set_column(col_num, col_num, column_width)
        
        # Format headers
        for col_num, column in enumerate(df.columns):
            worksheet.write(0, col_num, column, header_format)
    
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=f"transport_subscriptions_import_template.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# Create new registration link
@students_bp.route('/registration-links/create', methods=['GET', 'POST'])
@login_required
def create_registration_link():
    form = RegistrationLinkForm()
    
    if form.validate_on_submit():
        try:
            # Create PendingStudent record with token
            token = PendingStudent.generate_token()
            pending = PendingStudent(
                registration_token=token,
                notes=form.notes.data,
                status='pending',
                submission_date=datetime.now()
            )
            
            db.session.add(pending)
            db.session.commit()
            
            # Generate registration URL
            base_url = request.host_url.rstrip('/')
            registration_url = f"{base_url}/students/register/{token}"
            
            flash('تم إنشاء رابط التسجيل بنجاح!', 'success')
            return render_template('students/registration_link_created.html', 
                                 title='رابط التسجيل', 
                                 registration_url=registration_url,
                                 pending=pending)
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إنشاء رابط التسجيل: {str(e)}', 'danger')
            print(f"Error creating registration link: {e}")
    
    return render_template('students/create_registration_link.html', 
                         title='إنشاء رابط تسجيل جديد', 
                         form=form)

# Public registration form
@students_bp.route('/register/<token>', methods=['GET', 'POST'])
def register_student(token):
    # Check if token exists and is valid
    pending = PendingStudent.query.filter_by(registration_token=token).first()
    
    if not pending or pending.status != 'pending':
        flash('رابط التسجيل غير صالح أو منتهي الصلاحية.', 'danger')
        return render_template('students/invalid_registration.html', title='رابط غير صالح', now=datetime.now())
    
    form = StudentRegistrationForm()
    
    # Populate educational levels dropdown
    form.educational_level.choices = [(level.name, level.name) for level in 
                                     EducationalLevel.query.order_by(EducationalLevel.order).all()]
    
    # Pre-fill guardian info if available
    if request.method == 'GET':
        form.guardian_name.data = pending.guardian_name
        form.guardian_phone.data = pending.guardian_phone
        form.guardian_email.data = pending.guardian_email
        form.token.data = token
    
    if form.validate_on_submit():
        try:
            # Update pending student record with form data
            pending.first_name = form.first_name.data
            pending.last_name = form.last_name.data
            pending.gender = form.gender.data
            pending.massar_number = form.massar_number.data
            pending.birth_date = form.birth_date.data
            pending.educational_level = form.educational_level.data
            pending.institution = form.institution.data
            
            pending.guardian_name = form.guardian_name.data
            pending.guardian_national_id = form.guardian_national_id.data
            pending.guardian_phone = form.guardian_phone.data
            pending.guardian_email = form.guardian_email.data
            pending.address = form.address.data
            pending.notes = form.notes.data
            
            # Handle file uploads
            if form.student_photo.data:
                upload_dir = os.path.join('app/static/uploads/pending/photos')
                ensure_dir(upload_dir + '/')
                filename = secure_filename(f"{token}_photo_{form.student_photo.data.filename}")
                photo_path = os.path.join(upload_dir, filename)
                form.student_photo.data.save(photo_path)
                pending.student_photo = f"uploads/pending/photos/{filename}"
            
            if form.guardian_id_front.data:
                upload_dir = os.path.join('app/static/uploads/pending/documents')
                ensure_dir(upload_dir + '/')
                filename = secure_filename(f"{token}_id_front_{form.guardian_id_front.data.filename}")
                path = os.path.join(upload_dir, filename)
                form.guardian_id_front.data.save(path)
                pending.guardian_id_front = f"uploads/pending/documents/{filename}"
            
            if form.guardian_id_back.data:
                upload_dir = os.path.join('app/static/uploads/pending/documents')
                ensure_dir(upload_dir + '/')
                filename = secure_filename(f"{token}_id_back_{form.guardian_id_back.data.filename}")
                path = os.path.join(upload_dir, filename)
                form.guardian_id_back.data.save(path)
                pending.guardian_id_back = f"uploads/pending/documents/{filename}"
            
            if form.commitment_doc.data:
                upload_dir = os.path.join('app/static/uploads/pending/documents')
                ensure_dir(upload_dir + '/')
                filename = secure_filename(f"{token}_commitment_{form.commitment_doc.data.filename}")
                path = os.path.join(upload_dir, filename)
                form.commitment_doc.data.save(path)
                pending.commitment_doc = f"uploads/pending/documents/{filename}"
            
            db.session.commit()
            flash('تم إرسال طلب التسجيل بنجاح! سيتم مراجعته من قبل الإدارة.', 'success')
            return render_template('students/registration_success.html', title='تم إرسال الطلب بنجاح', now=datetime.now())
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء معالجة الطلب: {str(e)}', 'danger')
    
    return render_template('students/register.html', 
                         title='تسجيل طالب جديد', 
                         form=form,
                         token=token,
                         now=datetime.now())

# List pending registrations
@students_bp.route('/pending-registrations')
@login_required
def pending_registrations():
    pending_students = PendingStudent.query.order_by(PendingStudent.submission_date.desc()).all()
    return render_template('students/pending_registrations.html', 
                         title='طلبات التسجيل المعلقة',
                         pending_students=pending_students)

# View pending registration details
@students_bp.route('/pending-registrations/view/<int:id>')
@login_required
def view_pending_registration(id):
    pending = PendingStudent.query.get_or_404(id)
    # Create a simple form for CSRF protection
    form = FlaskForm()
    return render_template('students/view_pending_registration.html', 
                         title=f'طلب تسجيل: {pending.full_name}',
                         pending=pending,
                         form=form)

# Approve pending registration
@students_bp.route('/pending-registrations/approve/<int:id>', methods=['POST'])
@login_required
def approve_pending_registration(id):
    pending = PendingStudent.query.get_or_404(id)
    
    # Generate a new unique student ID - improved to ensure uniqueness
    def generate_unique_student_id():
        # Get the last student record
        last_student = Student.query.order_by(Student.student_id.desc()).first()
        
        if last_student and last_student.student_id.startswith('S') and last_student.student_id[1:].isdigit():
            # Extract the number part and increment it
            last_number = int(last_student.student_id[1:])
            new_id = f"S{str(last_number + 1).zfill(3)}"
        else:
            # If there are no students yet or the pattern is different, start with S001
            new_id = "S001"
        
        # Check if the generated ID already exists
        while Student.query.filter_by(student_id=new_id).first():
            # ID already exists, increment and try again
            if new_id.startswith('S') and new_id[1:].isdigit():
                number = int(new_id[1:])
                new_id = f"S{str(number + 1).zfill(3)}"
            else:
                # Fallback if something weird happens with the ID format
                new_id = f"S{str(random.randint(1000, 9999))}"
        
        return new_id
    
    # Get a guaranteed unique student ID
    new_student_id = generate_unique_student_id()
    
    # Create new student from pending registration
    student = Student(
        student_id=new_student_id,
        first_name=pending.first_name,
        last_name=pending.last_name,
        gender=pending.gender,
        massar_number=pending.massar_number,
        birth_date=pending.birth_date,
        educational_level=pending.educational_level,
        institution=pending.institution,
        monthly_fee=0,  # Default value, to be updated by admin
        guardian_name=pending.guardian_name,
        guardian_national_id=pending.guardian_national_id,
        guardian_phone=pending.guardian_phone,
        guardian_email=pending.guardian_email,
        address=pending.address,
        notes=pending.notes,
        status='active',
        registration_date=datetime.now().date()
    )
    
    # Copy uploaded files from pending to student folder
    if pending.student_photo:
        old_path = os.path.join('app/static', pending.student_photo)
        if os.path.exists(old_path):
            # Extract filename and create new path
            filename = os.path.basename(pending.student_photo)
            # Make filename splitting more robust
            filename_parts = filename.split('_', 2)
            # Check if we have enough parts before accessing them
            if len(filename_parts) >= 3:
                new_filename = secure_filename(f"{new_student_id}_{filename_parts[2]}")
            else:
                # Fallback: use original filename with new student ID
                new_filename = secure_filename(f"{new_student_id}_photo_{os.path.basename(filename)}")
            new_dir = os.path.join('app/static/uploads/students/photos')
            ensure_dir(new_dir + '/')
            new_path = os.path.join(new_dir, new_filename)
            
            # Copy file
            import shutil
            shutil.copy(old_path, new_path)
            student.student_photo = f"uploads/students/photos/{new_filename}"
    
    # Similar process for other documents
    for doc_type, src_field, dest_field in [
        ('id_front', 'guardian_id_front', 'guardian_id_front'),
        ('id_back', 'guardian_id_back', 'guardian_id_back'),
        ('commitment', 'commitment_doc', 'commitment_doc')
    ]:
        if getattr(pending, src_field):
            old_path = os.path.join('app/static', getattr(pending, src_field))
            if os.path.exists(old_path):
                filename = os.path.basename(getattr(pending, src_field))
                # Make filename splitting more robust
                filename_parts = filename.split('_', 3)
                # Check if we have enough parts before accessing them
                if len(filename_parts) >= 4:
                    new_filename = secure_filename(f"{new_student_id}_{doc_type}_{filename_parts[3]}")
                else:
                    # Fallback: use original filename with new student ID
                    new_filename = secure_filename(f"{new_student_id}_{doc_type}_{os.path.basename(filename)}")
                new_dir = os.path.join('app/static/uploads/students/documents')
                ensure_dir(new_dir + '/')
                new_path = os.path.join(new_dir, new_filename)
                
                import shutil
                shutil.copy(old_path, new_path)
                setattr(student, dest_field, f"uploads/students/documents/{new_filename}")
    
    # Update pending status
    pending.status = 'approved'
    
    # Save changes
    db.session.add(student)
    db.session.commit()
    
    flash(f'تمت الموافقة على طلب التسجيل وإضافة التلميذ {student.full_name} برقم {new_student_id} بنجاح!', 'success')
    return redirect(url_for('students.view', id=student.id))

# Reject pending registration
@students_bp.route('/pending-registrations/reject/<int:id>', methods=['POST'])
@login_required
def reject_pending_registration(id):
    pending = PendingStudent.query.get_or_404(id)
    reason = request.form.get('reject_reason', '')
    
    pending.status = 'rejected'
    pending.admin_notes = reason
    
    db.session.commit()
    flash('تم رفض طلب التسجيل.', 'warning')
    return redirect(url_for('students.pending_registrations')) 

# Delete pending registration
@students_bp.route('/pending-registrations/delete/<int:id>', methods=['POST'])
@login_required
def delete_pending_registration(id):
    pending = PendingStudent.query.get_or_404(id)
    
    # Delete associated files if they exist
    for attr in ['student_photo', 'guardian_id_front', 'guardian_id_back', 'commitment_doc']:
        if getattr(pending, attr):
            try:
                file_path = os.path.join('app/static', getattr(pending, attr))
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error removing file {attr}: {e}")
    
    db.session.delete(pending)
    db.session.commit()
    
    flash('تم حذف طلب التسجيل بنجاح.', 'success')
    return redirect(url_for('students.pending_registrations'))

# Add new routes for blacklist management
@students_bp.route('/blacklist')
@login_required
def blacklist():
    blacklisted_students = Student.query.filter_by(is_blacklisted=True).all()
    
    # Check for expired blacklist periods and automatically update
    today = datetime.now().date()
    for student in blacklisted_students:
        if student.blacklist_end_date and student.blacklist_end_date < today:
            student.is_blacklisted = False
            db.session.commit()
    
    # Refresh the query to get updated list
    blacklisted_students = Student.query.filter_by(is_blacklisted=True).all()
    
    return render_template('students/blacklist.html', 
                         title='القائمة السوداء', 
                         students=blacklisted_students,
                         now=datetime.now())

@students_bp.route('/add-to-blacklist/<int:id>', methods=['POST'])
@login_required
def add_to_blacklist(id):
    student = Student.query.get_or_404(id)
    
    blacklist_reason = request.form.get('blacklist_reason')
    blacklist_duration = int(request.form.get('blacklist_duration', 7))
    
    if not blacklist_reason:
        flash('يرجى تحديد سبب الإضافة إلى القائمة السوداء', 'danger')
        return redirect(url_for('students.view', id=student.id))
    
    # Set blacklist information
    student.is_blacklisted = True
    student.blacklist_reason = blacklist_reason
    student.blacklist_duration = blacklist_duration
    student.blacklist_start_date = datetime.now().date()
    student.blacklist_end_date = student.blacklist_start_date + timedelta(days=blacklist_duration)
    
    db.session.commit()
    
    flash(f'تمت إضافة التلميذ {student.full_name} إلى القائمة السوداء', 'warning')
    return redirect(url_for('students.blacklist'))

@students_bp.route('/remove-from-blacklist/<int:id>', methods=['POST'])
@login_required
def remove_from_blacklist(id):
    student = Student.query.get_or_404(id)
    
    # Remove from blacklist
    student.is_blacklisted = False
    
    db.session.commit()
    
    flash(f'تمت إزالة التلميذ {student.full_name} من القائمة السوداء', 'success')
    return redirect(url_for('students.blacklist'))

# Bulk delete students
@students_bp.route('/bulk-delete', methods=['POST'])
@login_required
def bulk_delete():
    student_ids = request.form.get('student_ids', '')
    if not student_ids:
        flash('لم يتم تحديد أي تلميذ للحذف', 'danger')
        return redirect(url_for('students.index'))
    
    # Split the comma-separated string into a list of IDs
    student_ids = student_ids.split(',')
    deleted_count = 0
    error_count = 0
    
    for id in student_ids:
        student = Student.query.get(id)
        if not student:
            continue
        
        # Check if there are related subscriptions
        if TransportSubscription.query.filter_by(student_id=id).count() > 0:
            error_count += 1
            continue
        
        # Remove files if they exist
        for attr in ['student_photo', 'guardian_id_front', 'guardian_id_back', 'commitment_doc']:
            if getattr(student, attr):
                try:
                    file_path = os.path.join('app/static', getattr(student, attr))
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except:
                    pass
        
        db.session.delete(student)
        deleted_count += 1
    
    db.session.commit()
    
    if deleted_count > 0:
        flash(f'تم حذف {deleted_count} تلميذ بنجاح', 'success')
    
    if error_count > 0:
        flash(f'لم يتم حذف {error_count} تلميذ بسبب وجود اشتراكات نقل مرتبطة بهم', 'warning')
    
    return redirect(url_for('students.index'))

# Bulk add to blacklist
@students_bp.route('/bulk-add-to-blacklist', methods=['POST'])
@login_required
def bulk_add_to_blacklist():
    student_ids = request.form.get('student_ids', '')
    blacklist_reason = request.form.get('blacklist_reason')
    blacklist_duration = int(request.form.get('blacklist_duration', 7))
    
    if not student_ids or not blacklist_reason:
        flash('يرجى تحديد التلاميذ وسبب الإضافة إلى القائمة السوداء', 'danger')
        return redirect(url_for('students.index'))
    
    # Split the comma-separated string into a list of IDs
    student_ids = student_ids.split(',')
    blacklisted_count = 0
    
    for id in student_ids:
        student = Student.query.get(id)
        if not student:
            continue
        
        # Set blacklist information
        student.is_blacklisted = True
        student.blacklist_reason = blacklist_reason
        student.blacklist_duration = blacklist_duration
        student.blacklist_start_date = datetime.now().date()
        student.blacklist_end_date = student.blacklist_start_date + timedelta(days=blacklist_duration)
        
        blacklisted_count += 1
    
    db.session.commit()
    
    if blacklisted_count > 0:
        flash(f'تمت إضافة {blacklisted_count} تلميذ إلى القائمة السوداء', 'warning')
    
    return redirect(url_for('students.blacklist'))

@students_bp.route('/educational-levels/<int:id>/update-field', methods=['POST'])
@login_required
def update_educational_level_field(id):
    try:
        data = request.get_json()
        field = data.get('field')
        value = data.get('value')
        
        if not field or value is None:
            return jsonify({'success': False, 'message': 'بيانات غير صالحة'}), 400
            
        level = EducationalLevel.query.get_or_404(id)
        
        if field == 'name':
            level.name = value
        elif field == 'order':
            level.order = int(value)
        elif field == 'description':
            level.description = value
        else:
            return jsonify({'success': False, 'message': 'حقل غير صالح'}), 400
            
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500