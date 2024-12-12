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

@bp.route('/')
def index():
    search = request.args.get('search', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    category_id = request.args.get('category_id', type=int)

    query = Event.query

    if search:
        search_term = f'%{search}%'
        query = query.filter(
            or_(
                Event.title.ilike(search_term),
                Event.description.ilike(search_term),
                Event.location_name.ilike(search_term),
                Event.street_name.ilike(search_term)
            )
        )

    if category_id:
        query = query.filter(Event.category_id == category_id)

    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Event.start_datetime >= start)
        except ValueError:
            flash('Invalid start date format', 'warning')

    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(Event.end_datetime <= end)
        except ValueError:
            flash('Invalid end date format', 'warning')

    events = query.order_by(Event.start_datetime).all()
    categories = Category.query.order_by(Category.name).all()

    # Debug logging
    if events:
        logger.info("Found events with coordinates:")
        for event in events:
            if event.latitude and event.longitude:
                logger.info(f"Event: {event.title} at [{event.latitude}, {event.longitude}]")
    else:
        logger.info("No events found")
    
    return render_template('index.html',
                          events=events,
                          categories=categories,
                          search=search,
                          start_date=start_date,
                          end_date=end_date,
                          selected_category=category_id)

@bp.route('/event/new', methods=['GET', 'POST'])
def create_event():
    form = EventForm()
    categories = Category.query.order_by(Category.name).all()
    form.category_id.choices = [(0, 'No Category')] + [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        try:
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

            address = get_full_address(event)
            if address:
                logger.info(f"Geocoding address: {address}")
                event.latitude, event.longitude = geocode_address(address)
                logger.info(f"Got coordinates: [{event.latitude}, {event.longitude}]")

            if form.file.data:
                file = form.file.data
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    event.file_path = filename

            db.session.add(event)
            db.session.commit()
            flash('Event created successfully!', 'success')
            return redirect(url_for('main.index'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating event: {str(e)}")
            flash('Error creating event. Please try again.', 'danger')

    return render_template('create_event.html', form=form)

@bp.route('/api/location-suggestions')
def location_suggestions():
    query = request.args.get('query', '')
    
    if len(query) < 3:
        return jsonify([])
    
    try:
        sleep(1)  # Respect Nominatim's usage policy
        url = 'https://nominatim.openstreetmap.org/search'
        headers = {
            'User-Agent': 'EventManagementApp/1.0',
            'Accept-Language': 'nl,en'
        }
        params = {
            'q': query,
            'format': 'json',
            'addressdetails': 1,
            'limit': 5,
            'countrycodes': 'nl'
        }

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        results = response.json()

        suggestions = []
        for result in results:
            address = result.get('address', {})
            suggestions.append({
                'address': result.get('display_name', ''),
                'postal_code': address.get('postcode', ''),
                'street': address.get('road', ''),
                'house_number': address.get('house_number', ''),
                'latitude': result.get('lat'),
                'longitude': result.get('lon')
            })

        return jsonify(suggestions)

    except Exception as e:
        logger.error(f"Error fetching location suggestions: {str(e)}")
        return jsonify([]), 500

def geocode_address(location_string):
    try:
        sleep(1)  # Respect Nominatim's usage policy
        url = 'https://nominatim.openstreetmap.org/search'
        headers = {
            'User-Agent': 'EventManagementApp/1.0',
            'Accept-Language': 'nl,en'
        }
        params = {
            'q': location_string,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1,
            'countrycodes': 'nl'
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if data and len(data) > 0:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return lat, lon
            
        return None, None

    except Exception as e:
        logger.error(f"Geocoding error: {str(e)}")
        return None, None

def get_full_address(event):
    parts = []
    if event.street_name:
        street = event.street_name.strip()
        if event.street_number:
            street += f' {event.street_number.strip()}'
        parts.append(street)
    if event.postal_code:
        parts.append(event.postal_code.strip())
    if event.location_name:
        parts.append(event.location_name.strip())
    
    address = ', '.join(filter(None, parts))
    return address if address else None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf', 'png', 'jpg', 'jpeg'}
