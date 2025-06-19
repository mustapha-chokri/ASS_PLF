from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.models.educational_level import EducationalLevel
from app.extensions import db
from app.forms.educational_level import EducationalLevelForm

bp = Blueprint('students', __name__)

@bp.route('/educational-levels')
@login_required
def educational_levels():
    levels = EducationalLevel.query.order_by(EducationalLevel.order).all()
    form = EducationalLevelForm()
    edit_form = EducationalLevelForm()
    return render_template('students/educational_levels.html', 
                         title='المستويات الدراسية',
                         levels=levels,
                         form=form,
                         edit_form=edit_form)

@bp.route('/educational-levels/add', methods=['POST'])
@login_required
def add_educational_level():
    form = EducationalLevelForm()
    if form.validate_on_submit():
        level = EducationalLevel(
            name=form.name.data,
            order=form.order.data,
            description=form.description.data
        )
        db.session.add(level)
        db.session.commit()
        flash('تم إضافة المستوى الدراسي بنجاح', 'success')
    return redirect(url_for('students.educational_levels'))

@bp.route('/educational-levels/<int:id>/edit', methods=['POST'])
@login_required
def edit_educational_level(id):
    level = EducationalLevel.query.get_or_404(id)
    form = EducationalLevelForm()
    if form.validate_on_submit():
        level.name = form.name.data
        level.order = form.order.data
        level.description = form.description.data
        db.session.commit()
        flash('تم تحديث المستوى الدراسي بنجاح', 'success')
    return redirect(url_for('students.educational_levels'))

@bp.route('/educational-levels/<int:id>/delete')
@login_required
def delete_educational_level(id):
    level = EducationalLevel.query.get_or_404(id)
    db.session.delete(level)
    db.session.commit()
    flash('تم حذف المستوى الدراسي بنجاح', 'success')
    return redirect(url_for('students.educational_levels'))

@bp.route('/educational-levels/<int:id>/update-field', methods=['POST'])
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