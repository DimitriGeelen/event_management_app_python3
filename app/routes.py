import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Event
from app.forms import EventForm
import requests
from time import sleep

bp = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'png', 'jpg', 'jpeg'}

def geocode_address(location_string):
    """Geocode an address using Nominatim"""
    try:
        # Add a small delay to respect Nominatim's usage policy
        sleep(1)

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
        else:
            print(f"No results found for {location_string}")
            # Try with simplified address
            simplified_address = simplify_address(location_string)
            if simplified_address != location_string:
                print(f"Trying with simplified address: {simplified_address}")
                return geocode_address(simplified_address)
            return None, None
    except Exception as e:
        print(f"Geocoding error for {location_string}: {str(e)}")
        return None, None

def simplify_address(address):
    """Remove unnecessary parts of the address to improve geocoding success"""
    # Split address into parts
    parts = address.split(',')
    # Take only the street address and postal code if available
    if len(parts) > 2:
        return ', '.join(parts[:2]).strip()
    return address

def get_full_address(event):
    """Combine address components into a single string"""
    address_parts = []
    
    # Add street and number first
    if event.street_name:
        street = event.street_name.strip()
        if event.street_number:
            street += f' {event.street_number.strip()}'
        address_parts.append(street)
    
    # Add postal code
    if event.postal_code:
        address_parts.append(event.postal_code.strip())
    
    # Add location name
    if event.location_name:
        address_parts.append(event.location_name.strip())
    
    full_address = ', '.join(filter(None, address_parts))
    print(f"Constructed full address: {full_address}")
    return full_address

@bp.route('/')
def index():
    events = Event.query.order_by(Event.start_datetime).all()
    # Print event coordinates for debugging
    for event in events:
        print(f"Event {event.title}: lat={event.latitude}, lon={event.longitude}")
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
            print(f"Attempting to geocode address: {address}")
            event.latitude, event.longitude = geocode_address(address)
            print(f"Got coordinates: lat={event.latitude}, lon={event.longitude}")
            
            # If geocoding failed, try with just the street address
            if event.latitude is None and event.street_name:
                street_address = f"{event.street_name} {event.street_number}, {event.postal_code}"
                print(f"Retrying with street address only: {street_address}")
                event.latitude, event.longitude = geocode_address(street_address)
        
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

[Rest of the file remains the same...]