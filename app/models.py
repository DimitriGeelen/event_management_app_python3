from app import db
from datetime import datetime

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    location_name = db.Column(db.String(100))
    street_name = db.Column(db.String(100))
    street_number = db.Column(db.String(20))
    postal_code = db.Column(db.String(20))
    file_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Add coordinates for map
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_datetime': self.start_datetime.isoformat(),
            'end_datetime': self.end_datetime.isoformat(),
            'location_name': self.location_name,
            'street_name': self.street_name,
            'street_number': self.street_number,
            'postal_code': self.postal_code,
            'file_path': self.file_path,
            'latitude': self.latitude,
            'longitude': self.longitude
        }