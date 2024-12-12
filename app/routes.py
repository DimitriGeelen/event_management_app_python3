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
import logging

bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@bp.route('/event/new', methods=['GET', 'POST'])
def create_event():
    form = EventForm()
    
    # Populate category choices
    categories = Category.query.order_by(Category.name).all()
    form.category_id.choices = [(0, 'No Category')] + [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            start_datetime=form.start_datetime.data,
            end_datetime=form.end_datetime.data,
            location_name=form.location_name.data,
            street_name=form.street_name.data,
            street_number=form.street_number.data,
            postal_code=form.postal_code.data,
            category_id=form.category_id.data if form.category_id.data != 0 else None
        )
        
        # Geocode the address
        address = get_full_address(event)
        if address:
            print(f"Attempting to geocode address: {address}")
            try:
                event.latitude, event.longitude = geocode_address(address)
                print(f"Got coordinates: lat={event.latitude}, lon={event.longitude}")
            except Exception as e:
                logger.error(f"Geocoding error: {str(e)}")
                flash('Error geocoding address', 'warning')
        
        if form.file.data:
            file = form.file.data
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                event.file_path = filename
        
        try:
            db.session.add(event)
            db.session.commit()
            flash('Event created successfully!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating event: {str(e)}")
            flash('Error creating event', 'danger')
    
    return render_template('create_event.html', form=form)

# Add the rest of your existing routes here...
