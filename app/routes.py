import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Event, Category
from app.forms import EventForm, CategoryForm
import requests
from datetime import datetime
from sqlalchemy import or_
from time import sleep

bp = Blueprint('main', __name__)

# Category routes
@bp.route('/categories')
def categories():
    categories = Category.query.order_by(Category.name).all()
    form = CategoryForm()
    return render_template('categories.html', categories=categories, form=form)

@bp.route('/category/add', methods=['POST'])
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, description=form.description.data)
        db.session.add(category)
        try:
            db.session.commit()
            flash('Category added successfully!', 'success')
        except:
            db.session.rollback()
            flash('A category with this name already exists.', 'danger')
    return redirect(url_for('main.categories'))

@bp.route('/category/<int:id>/edit', methods=['POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    if request.form.get('name'):
        category.name = request.form['name']
        category.description = request.form.get('description', '')
        try:
            db.session.commit()
            flash('Category updated successfully!', 'success')
        except:
            db.session.rollback()
            flash('A category with this name already exists.', 'danger')
    return redirect(url_for('main.categories'))

@bp.route('/category/<int:id>/delete', methods=['POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    events = Event.query.filter_by(category_id=id).all()
    for event in events:
        event.category_id = None
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('main.categories'))

# Existing routes...
[Previous route code continues here...]