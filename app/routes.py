import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Event
from app.forms import EventForm
import requests
from datetime import datetime
from sqlalchemy import or_
from time import sleep

bp = Blueprint('main', __name__)

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

@bp.route('/')
def index():
    # Get search parameters
    search = request.args.get('search', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

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
    return render_template('index.html', events=events, search=search,
                         start_date=start_date, end_date=end_date)

@bp.route('/event/new', methods=['GET', 'POST'])
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            start_datetime=form.start_datetime.data,
            end_datetime=form.end_datetime.data,
            location_name=form.location_name.data,
            street_name=form.street_name.data,
            street_number=form.street_number.data,
            postal_code=form.postal_code.data
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
    
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.start_datetime = form.start_datetime.data
        event.end_datetime = form.end_datetime.data
        event.location_name = form.location_name.data
        event.street_name = form.street_name.data
        event.street_number = form.street_number.data
        event.postal_code = form.postal_code.data
        
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
    if len(query) < 3:
        return jsonify([])
    
    url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': query,
        'format': 'json',
        'addressdetails': 1,
        'limit': 5
    }
    headers = {
        'User-Agent': current_app.config.get('NOMINATIM_USER_AGENT', 'EventManagementApp/1.0')
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        results = response.json()
        
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
        
        return jsonify(suggestions)
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f'Error fetching location suggestions: {str(e)}')
        return jsonify([]), 500