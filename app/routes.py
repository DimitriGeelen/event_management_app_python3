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
    # Get all events and print their data for debugging
    events = Event.query.order_by(Event.start_datetime).all()
    print("\nEvent Data:")
    for event in events:
        print(f"Event: {event.title}")
        print(f"Location: {event.location_name}, {event.street_name} {event.street_number}, {event.postal_code}")
        print(f"Coordinates: lat={event.latitude}, lon={event.longitude}\n")

    categories = Category.query.order_by(Category.name).all()
    return render_template('index.html', events=events, categories=categories)

[... rest of your routes.py file ...]