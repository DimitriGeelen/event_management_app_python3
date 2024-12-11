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

[... rest of your routes.py file remains the same ...]
