import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Event
from app.forms import EventForm
import requests

bp = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'png', 'jpg', 'jpeg'}

def geocode_address(location_string):
    """Geocode an address using Nominatim"""
    try:
        url = 'https://nominatim.openstreetmap.org/search'
        headers = {'User-Agent': current_app.config.get('NOMINATIM_USER_AGENT', 'EventManagementApp/1.0')}
        params = {
            'q': location_string,
            'format': 'json',
            'limit': 1
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            return float(data[0]['lat']), float(data[0]['lon'])
        return None, None
    except Exception as e:
        current_app.logger.error(f'Geocoding error: {str(e)}')
        return None, None

def get_full_address(event):
    """Combine address components into a single string"""
    address_parts = []
    if event.location_name:
        address_parts.append(event.location_name)
    if event.street_name:
        street = event.street_name
        if event.street_number:
            street += f' {event.street_number}'
        address_parts.append(street)
    if event.postal_code:
        address_parts.append(event.postal_code)
    return ', '.join(address_parts)

@bp.route('/')
def index():
    events = Event.query.order_by(Event.start_datetime).all()
    return render_template('index.html', events=events)

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
            event.latitude, event.longitude = geocode_address(address)
        
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
            event.latitude, event.longitude = geocode_address(address)
        
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