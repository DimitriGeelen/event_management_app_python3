import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Event
from app.forms import EventForm
import requests
from datetime import datetime
from sqlalchemy import or_

bp = Blueprint('main', __name__)

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

    # Order by start_datetime
    events = query.order_by(Event.start_datetime).all()
    
    # Print event coordinates for debugging
    for event in events:
        print(f"Event {event.title}: lat={event.latitude}, lon={event.longitude}")
    
    return render_template('index.html', 
                           events=events,
                           search=search,
                           start_date=start_date,
                           end_date=end_date)

# Rest of the file remains the same...