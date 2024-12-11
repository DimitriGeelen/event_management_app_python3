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
    # Get search parameters
    search = request.args.get('search', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    category_id = request.args.get('category_id', type=int)

    # Base query
    query = Event.query

    # Apply search filter if provided
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

    # Apply category filter
    if category_id:
        query = query.filter(Event.category_id == category_id)

    # Apply date filters if provided
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
    
    return render_template('index.html', 
                          events=events,
                          categories=categories,
                          search=search,
                          start_date=start_date,
                          end_date=end_date,
                          selected_category=category_id)

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
            event.latitude, event.longitude = geocode_address(address)
            print(f"Got coordinates: lat={event.latitude}, lon={event.longitude}")
        
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
    
    return render_template('create_event.html', form=form)

@bp.route('/event/<int:id>/edit', methods=['GET', 'POST'])
def edit_event(id):
    event = Event.query.get_or_404(id)
    form = EventForm(obj=event)
    
    # Populate category choices
    categories = Category.query.order_by(Category.name).all()
    form.category_id.choices = [(0, 'No Category')] + [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.start_datetime = form.start_datetime.data
        event.end_datetime = form.end_datetime.data
        event.location_name = form.location_name.data
        event.street_name = form.street_name.data
        event.street_number = form.street_number.data
        event.postal_code = form.postal_code.data
        event.category_id = form.category_id.data if form.category_id.data != 0 else None
        
        # Update geocoding
        address = get_full_address(event)
        if address:
            print(f"Attempting to geocode address: {address}")
            event.latitude, event.longitude = geocode_address(address)
            print(f"Got coordinates: lat={event.latitude}, lon={event.longitude}")
        
        if form.file.data:
            file = form.file.data
            if file and allowed_file(file.filename):
                if event.file_path:
                    old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], event.file_path)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                event.file_path = filename
        
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('edit_event.html', form=form, event=event)

@bp.route('/event/<int:id>/delete', methods=['POST'])
def delete_event(id):
    event = Event.query.get_or_404(id)
    
    if event.file_path:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], event.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('main.index'))

@bp.route('/api/location-suggestions')
def location_suggestions():
    query = request.args.get('query', '')
    logger.info(f"Received location query: {query}")
    
    if len(query) < 3:
        return jsonify([])
    
    # OpenStreetMap Nominatim API endpoint
    url = 'https://nominatim.openstreetmap.org/search'
    
    # Parameters for the API request
    params = {
        'q': query,
        'format': 'json',
        'addressdetails': 1,
        'limit': 5
    }
    
    # Headers including User-Agent as required by OpenStreetMap
    headers = {
        'User-Agent': 'EventManagementApp/1.0',
        'Accept-Language': 'en,de'
    }
    
    try:
        # Add a small delay to respect Nominatim's usage policy
        sleep(1)
        
        logger.info(f"Sending request to Nominatim: {url} with params {params}")
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        results = response.json()
        logger.info(f"Received {len(results)} results from Nominatim")
        
        suggestions = []
        for result in results:
            address = result.get('address', {})
            suggestion = {
                'address': result.get('display_name', ''),
                'postal_code': address.get('postcode', ''),
                'street': address.get('road', ''),
                'house_number': address.get('house_number', ''),
                'latitude': result.get('lat'),
                'longitude': result.get('lon')
            }
            suggestions.append(suggestion)
            logger.debug(f"Processed suggestion: {suggestion}")
        
        return jsonify(suggestions)
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching location suggestions: {str(e)}")
        return jsonify({'error': 'Failed to fetch location suggestions'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in location suggestions: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'png', 'jpg', 'jpeg'}

def geocode_address(location_string):
    try:
        sleep(1)  # Respect Nominatim's usage policy
        url = 'https://nominatim.openstreetmap.org/search'
        headers = {
            'User-Agent': 'EventManagementApp/1.0 (info@example.com)',
            'Accept-Language': 'en,de'
        }
        params = {
            'q': location_string,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }
        
        print(f"Sending geocoding request for: {location_string}")
        response = requests.get(url, headers=headers, params=params)
        print(f"Response status code: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        print(f"Geocoding response: {data}")
        
        if data and len(data) > 0:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            print(f"Successfully geocoded {location_string}: lat={lat}, lon={lon}")
            return lat, lon
        print(f"No results found for {location_string}")
        return None, None
    except Exception as e:
        print(f"Geocoding error for {location_string}: {str(e)}")
        return None, None

def get_full_address(event):
    address_parts = []
    if event.street_name:
        street = event.street_name.strip()
        if event.street_number:
            street += f' {event.street_number.strip()}'
        address_parts.append(street)
    if event.postal_code:
        address_parts.append(event.postal_code.strip())
    if event.location_name:
        address_parts.append(event.location_name.strip())
    full_address = ', '.join(filter(None, address_parts))
    print(f"Constructed full address: {full_address}")
    return full_address