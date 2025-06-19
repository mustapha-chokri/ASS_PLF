from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app import db
from app.controllers.members import members_bp
from app.models.member import Member, MembershipApplication
from app.models.subscription import Subscription
from app.controllers.members.forms import MemberForm, MembershipApplicationForm, SubscriptionForm
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from wtforms import SelectField
from wtforms.validators import DataRequired
import secrets
import string
import sqlite3
from flask_wtf import FlaskForm

# Variable globale pour suivre le nombre de nouvelles demandes
new_applications_count = 0

@members_bp.route('/')
@login_required
def index():
    members = Member.query.all()
    return render_template('members/index.html', title='لائحة المنخرطين', members=members)

@members_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = MemberForm()
    if form.validate_on_submit():
        # Generate registration number
        year = datetime.now().year
        last_member = Member.query.order_by(Member.id.desc()).first()
        reg_number = f"{year}-{(last_member.id + 1 if last_member else 1):04d}"
        
        member = Member(
            registration_number=reg_number,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            national_id=form.national_id.data,
            birth_date=form.birth_date.data,
            address=form.address.data,
            city=form.city.data,
            phone=form.phone.data,
            email=form.email.data,
            profession=form.profession.data,
            join_date=form.join_date.data,
            status='active',
            notes=form.notes.data
        )
        
        # Handle photo upload
        if form.photo.data:
            # Ensure uploads directory exists
            upload_dir = os.path.join('app/static/uploads/members')
            os.makedirs(upload_dir, exist_ok=True)
            
            filename = secure_filename(f"{reg_number}_{form.photo.data.filename}")
            photo_path = os.path.join(upload_dir, filename)
            form.photo.data.save(photo_path)
            member.photo_path = f"uploads/members/{filename}"
        
        db.session.add(member)
        db.session.commit()
        flash('تمت إضافة المنخرط بنجاح!', 'success')
        return redirect(url_for('members.index'))
    
    return render_template('members/add.html', title='إضافة منخرط جديد', form=form)

@members_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    member = Member.query.get_or_404(id)
    form = MemberForm(obj=member)
    
    if form.validate_on_submit():
        member.first_name = form.first_name.data
        member.last_name = form.last_name.data
        member.national_id = form.national_id.data
        member.birth_date = form.birth_date.data
        member.address = form.address.data
        member.city = form.city.data
        member.phone = form.phone.data
        member.email = form.email.data
        member.profession = form.profession.data
        member.join_date = form.join_date.data
        member.status = form.status.data
        member.notes = form.notes.data
        
        # Handle photo upload
        if form.photo.data:
            # Ensure uploads directory exists
            upload_dir = os.path.join('app/static/uploads/members')
            os.makedirs(upload_dir, exist_ok=True)
            
            filename = secure_filename(f"{member.registration_number}_{form.photo.data.filename}")
            photo_path = os.path.join(upload_dir, filename)
            form.photo.data.save(photo_path)
            
            # Remove old photo if exists
            if member.photo_path:
                try:
                    old_photo_path = os.path.join('app/static', member.photo_path)
                    if os.path.exists(old_photo_path):
                        os.remove(old_photo_path)
                except:
                    pass
                    
            member.photo_path = f"uploads/members/{filename}"
        
        db.session.commit()
        flash('تم تحديث بيانات المنخرط بنجاح!', 'success')
        return redirect(url_for('members.view', id=member.id))
    
    return render_template('members/edit.html', title='تعديل بيانات منخرط', form=form, member=member)

@members_bp.route('/view/<int:id>')
@login_required
def view(id):
    member = Member.query.get_or_404(id)
    subscriptions = Subscription.query.filter_by(member_id=id).order_by(Subscription.year.desc()).all()
    return render_template('members/view.html', title=f'بيانات المنخرط: {member.full_name}', 
                          member=member, subscriptions=subscriptions)

@members_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    member = Member.query.get_or_404(id)
    
    # Check if there are related subscriptions
    if member.subscriptions.count() > 0:
        flash('لا يمكن حذف هذا المنخرط لوجود اشتراكات مرتبطة به', 'danger')
        return redirect(url_for('members.view', id=member.id))
    
    # Remove photo if exists
    if member.photo_path:
        try:
            photo_path = os.path.join('app/static', member.photo_path)
            if os.path.exists(photo_path):
                os.remove(photo_path)
        except:
            pass
    
    db.session.delete(member)
    db.session.commit()
    flash('تم حذف المنخرط بنجاح', 'success')
    return redirect(url_for('members.index'))

# Membership Cards
@members_bp.route('/cards')
@login_required
def cards():
    members = Member.query.filter_by(status='active').all()
    return render_template('members/cards.html', title='بطاقات الانخراط', members=members)

@members_bp.route('/card/<int:id>')
@login_required
def print_card(id):
    member = Member.query.get_or_404(id)
    return render_template('members/print_card.html', title=f'بطاقة الانخراط: {member.full_name}', member=member)

@members_bp.route('/cards/print')
@login_required
def print_multiple_cards():
    member_ids = request.args.get('ids', '')
    if member_ids:
        ids = [int(id) for id in member_ids.split(',') if id.isdigit()]
        members = Member.query.filter(Member.id.in_(ids)).all()
    else:
        members = []
    
    return render_template('members/print_multiple_cards.html', 
                          title='طباعة بطاقات المنخرطين',
                          members=members)

# Membership Applications
@members_bp.route('/applications')
@login_required
def applications():
    # Réinitialiser le compteur de nouvelles demandes
    global new_applications_count
    new_applications_count = 0
    
    applications = MembershipApplication.query.order_by(MembershipApplication.application_date.desc()).all()
    return render_template('members/applications.html', title='طلبات الانخراط', applications=applications)

@members_bp.route('/applications/add', methods=['GET', 'POST'])
@login_required
def add_application():
    form = MembershipApplicationForm()
    if form.validate_on_submit():
        application = MembershipApplication(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            national_id=form.national_id.data,
            birth_date=form.birth_date.data,
            address=form.address.data,
            phone=form.phone.data,
            email=form.email.data,
            profession=form.profession.data,
            application_date=datetime.now().date(),
            status='pending',
            notes=form.notes.data
        )
        
        db.session.add(application)
        db.session.commit()
        flash('تم تقديم طلب الانخراط بنجاح!', 'success')
        return redirect(url_for('members.applications'))
    
    return render_template('members/add_application.html', title='تقديم طلب انخراط', form=form)

@members_bp.route('/applications/approve/<int:id>', methods=['GET', 'POST'])
@login_required
def approve_application(id):
    application = MembershipApplication.query.get_or_404(id)
    
    if application.status != 'pending':
        flash('تم معالجة هذا الطلب مسبقاً', 'warning')
        return redirect(url_for('members.applications'))
    
    # Create new member from application
    year = datetime.now().year
    last_member = Member.query.order_by(Member.id.desc()).first()
    reg_number = f"{year}-{(last_member.id + 1 if last_member else 1):04d}"
    
    member = Member(
        registration_number=reg_number,
        first_name=application.first_name,
        last_name=application.last_name,
        national_id=application.national_id,
        birth_date=application.birth_date,
        address=application.address,
        phone=application.phone,
        email=application.email,
        profession=application.profession,
        join_date=datetime.now().date(),
        status='active',
        notes=application.notes
    )
    
    # Update application status
    application.status = 'approved'
    application.reviewed_by = current_user.id
    application.review_date = datetime.now()
    
    db.session.add(member)
    db.session.commit()
    
    flash('تمت الموافقة على طلب الانخراط وإضافة المنخرط الجديد بنجاح!', 'success')
    return redirect(url_for('members.view', id=member.id))

@members_bp.route('/applications/reject/<int:id>', methods=['POST'])
@login_required
def reject_application(id):
    application = MembershipApplication.query.get_or_404(id)
    
    if application.status != 'pending':
        flash('تم معالجة هذا الطلب مسبقاً', 'warning')
        return redirect(url_for('members.applications'))
    
    application.status = 'rejected'
    application.reviewed_by = current_user.id
    application.review_date = datetime.now()
    
    db.session.commit()
    flash('تم رفض طلب الانخراط', 'success')
    return redirect(url_for('members.applications'))

# Subscriptions
@members_bp.route('/subscriptions')
@login_required
def subscriptions():
    # Get statistics for the dashboard
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    yearly_subscriptions = Subscription.query.filter(Subscription.year == current_year).count()
    yearly_amount = db.session.query(db.func.sum(Subscription.amount)).filter(Subscription.year == current_year).scalar() or 0
    
    monthly_subscriptions = Subscription.query.filter(
        Subscription.payment_date >= datetime(current_year, current_month, 1),
        Subscription.payment_date < datetime(current_year, current_month + 1, 1) if current_month < 12 else datetime(current_year + 1, 1, 1)
    ).count()
    
    monthly_amount = db.session.query(db.func.sum(Subscription.amount)).filter(
        Subscription.payment_date >= datetime(current_year, current_month, 1),
        Subscription.payment_date < datetime(current_year, current_month + 1, 1) if current_month < 12 else datetime(current_year + 1, 1, 1)
    ).scalar() or 0
    
    subscriptions = Subscription.query.order_by(Subscription.payment_date.desc()).all()
    return render_template('members/subscriptions.html', 
                          title='إدارة الاشتراكات', 
                          subscriptions=subscriptions,
                          yearly_subscriptions=yearly_subscriptions,
                          yearly_amount=yearly_amount,
                          monthly_subscriptions=monthly_subscriptions,
                          monthly_amount=monthly_amount)

@members_bp.route('/subscriptions/add', methods=['GET', 'POST'])
@login_required
def add_subscription():
    form = SubscriptionForm()
    # Add a member selection field
    form.member_id = SelectField('المنخرط', coerce=int, validators=[DataRequired()])
    # Populate the member choices
    form.member_id.choices = [(m.id, m.full_name) for m in Member.query.filter_by(status='active').order_by(Member.first_name).all()]
    
    if form.validate_on_submit():
        subscription = Subscription(
            member_id=form.member_id.data,
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
        flash('تم تسجيل الاشتراك بنجاح!', 'success')
        return redirect(url_for('members.subscriptions'))
    
    # Pre-fill the current year
    if form.year.data is None:
        form.year.data = datetime.now().year
    
    return render_template('members/add_subscription.html', title='إضافة اشتراك جديد', form=form)

@members_bp.route('/subscriptions/add/<int:member_id>', methods=['GET', 'POST'])
@login_required
def add_member_subscription(member_id):
    member = Member.query.get_or_404(member_id)
    form = SubscriptionForm()
    
    if form.validate_on_submit():
        subscription = Subscription(
            member_id=member.id,
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
        flash('تم تسجيل الاشتراك بنجاح!', 'success')
        return redirect(url_for('members.view', id=member.id))
    
    # Pre-fill the current year
    if form.year.data is None:
        form.year.data = datetime.now().year
    
    return render_template('members/add_subscription.html', title='إضافة اشتراك جديد', 
                          form=form, member=member)

@members_bp.route('/subscription/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_subscription(id):
    subscription = Subscription.query.get_or_404(id)
    form = SubscriptionForm(obj=subscription)
    
    if form.validate_on_submit():
        subscription.year = form.year.data
        subscription.amount = form.amount.data
        subscription.payment_date = form.payment_date.data
        subscription.payment_method = form.payment_method.data
        subscription.receipt_number = form.receipt_number.data
        subscription.notes = form.notes.data
        
        db.session.commit()
        flash('تم تعديل الاشتراك بنجاح!', 'success')
        return redirect(url_for('members.view', id=subscription.member_id))
    
    return render_template('members/subscription_form.html', 
                           title='تعديل اشتراك', 
                           form=form,
                           member=subscription.member)

@members_bp.route('/subscription/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_subscription(id):
    subscription = Subscription.query.get_or_404(id)
    member_id = subscription.member_id
    
    db.session.delete(subscription)
    db.session.commit()
    
    flash('تم حذف الاشتراك بنجاح!', 'success')
    return redirect(url_for('members.view', id=member_id))

@members_bp.route('/subscription/receipt/<int:id>')
@login_required
def print_receipt(id):
    subscription = Subscription.query.get_or_404(id)
    return render_template('members/print_receipt.html', 
                          title='طباعة إيصال', 
                          subscription=subscription)

# Route publique pour soumettre une nouvelle demande d'adhésion
@members_bp.route('/public/apply/<token>', methods=['GET', 'POST'])
def public_application(token):
    """
    Route publique qui permet aux visiteurs de soumettre une demande d'adhésion
    en utilisant un lien unique avec un token.
    """
    # Vérifier si le token est valide
    application = MembershipApplication.query.filter_by(application_token=token).first()
    
    if not application or application.status != 'pending_link':
        # Mostrar una página de error personalizada en lugar de redirigir al panel principal
        return render_template('members/invalid_token.html', 
                              title='رابط غير صالح',
                              current_year=datetime.now().year)
    
    form = MembershipApplicationForm()
    
    if form.validate_on_submit():
        global new_applications_count
        
        # التأكد من إدخال جميع البيانات الإلزامية
        if not form.national_id.data:
            flash('يجب إدخال رقم البطاقة الوطنية.', 'danger')
            return render_template('members/public_application.html', 
                             title='تقديم طلب انخراط جديد', 
                             form=form,
                             application_token=token,
                             current_year=datetime.now().year)
        
        # Mettre à jour les informations de l'application avec les données du formulaire
        application.first_name = form.first_name.data
        application.last_name = form.last_name.data
        application.national_id = form.national_id.data
        application.birth_date = form.birth_date.data
        application.address = form.address.data
        application.phone = form.phone.data
        application.email = form.email.data
        application.profession = form.profession.data
        application.status = 'pending'  # Changer de 'pending_link' à 'pending'
        application.notes = form.notes.data
        
        db.session.commit()
        
        # Incrémenter le compteur de nouvelles demandes
        new_applications_count += 1
        
        flash('تم تقديم طلب الانخراط بنجاح! سيتم مراجعة طلبك قريباً.', 'success')
        return render_template('members/application_success.html', 
                             title='تم تقديم الطلب بنجاح',
                             current_year=datetime.now().year)
    
    return render_template('members/public_application.html', 
                         title='تقديم طلب انخراط جديد', 
                         form=form,
                         application_token=token,
                         current_year=datetime.now().year)

@members_bp.route('/application/create_link', methods=['GET', 'POST'])
@login_required
def create_application_link():
    """
    Crée un nouveau lien d'application à envoyer à un membre potentiel.
    """
    form = FlaskForm()  # Create a simple form for CSRF protection
    
    if form.validate_on_submit():
        # Générer un token unique
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        
        # Créer une nouvelle application avec le statut 'pending_link'
        application = MembershipApplication(
            first_name='',  # Sera rempli par l'utilisateur
            last_name='',
            phone='',  # ضروري أن تكون سلسلة فارغة وليس NULL
            national_id='',  # القيمة الفارغة بدلاً من NULL
            application_date=datetime.now().date(),
            status='pending_link',  # Statut spécial pour les liens en attente
            application_token=token
        )
        
        db.session.add(application)
        db.session.commit()
        
        # Générer le lien complet
        application_link = url_for('members.public_application', token=token, _external=True)
        
        return render_template('members/application_link_created.html',
                              title='تم إنشاء رابط طلب الانخراط',
                              application_link=application_link,
                              current_year=datetime.now().year)
    
    return render_template('members/create_application_link.html',
                          title='إنشاء رابط طلب انخراط',
                          current_year=datetime.now().year,
                          form=form)

@members_bp.route('/applications/links')
@login_required
def application_links():
    """
    Affiche tous les liens d'application créés et leur statut.
    """
    # Récupérer toutes les applications avec un token
    applications = MembershipApplication.query.filter(
        MembershipApplication.application_token.isnot(None)
    ).order_by(MembershipApplication.application_date.desc()).all()
    
    return render_template('members/application_links.html',
                          title='روابط طلبات الانخراط',
                          applications=applications)

# API pour vérifier les nouvelles demandes
@members_bp.route('/api/check_new_applications', methods=['GET'])
@login_required
def check_new_applications():
    """API qui renvoie le nombre de nouvelles demandes d'adhésion."""
    global new_applications_count
    count = new_applications_count
    return jsonify({'count': count})

# API pour réinitialiser le compteur de nouvelles demandes
@members_bp.route('/api/reset_applications_count', methods=['POST'])
@login_required
def reset_applications_count():
    """Réinitialise le compteur de nouvelles demandes après que l'utilisateur les a consultées."""
    global new_applications_count
    new_applications_count = 0
    return jsonify({'success': True})

@members_bp.route('/update_schema', methods=['GET'])
@login_required
def update_schema():
    """Route temporaire pour mettre à jour le schéma de la base de données."""
    try:
        # Vérifier si l'utilisateur est administrateur
        if not current_user.is_admin:
            flash('Vous n\'avez pas les droits pour effectuer cette opération.', 'danger')
            return redirect(url_for('dashboard.index'))
            
        # Ajouter la colonne application_token si elle n'existe pas déjà
        conn = sqlite3.connect('app/association.db')
        cursor = conn.cursor()
        
        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(membership_applications)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'application_token' not in columns:
            cursor.execute("ALTER TABLE membership_applications ADD COLUMN application_token TEXT")
            conn.commit()
            flash('La base de données a été mise à jour avec succès.', 'success')
        else:
            flash('Le schéma de la base de données est déjà à jour.', 'info')
        
        conn.close()
        return redirect(url_for('dashboard.index'))
        
    except Exception as e:
        flash(f'Une erreur est survenue lors de la mise à jour du schéma: {str(e)}', 'danger')
        return redirect(url_for('dashboard.index')) 