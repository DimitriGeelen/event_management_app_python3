from app import db
from datetime import datetime

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    events = db.relationship('Event', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

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
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    
    def to_dict(self):
        # Build location string
        location_parts = []
        if self.location_name:
            location_parts.append(self.location_name)
        if self.street_name:
            street = self.street_name
            if self.street_number:
                street += f' {self.street_number}'
            location_parts.append(street)
        if self.postal_code:
            location_parts.append(self.postal_code)
            
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_datetime': self.start_datetime.strftime('%Y-%m-%d %H:%M'),
            'end_datetime': self.end_datetime.strftime('%Y-%m-%d %H:%M'),
            'location_name': self.location_name,
            'street_name': self.street_name,
            'street_number': self.street_number,
            'postal_code': self.postal_code,
            'location': ', '.join(location_parts),
            'file_path': self.file_path,
            'latitude': float(self.latitude) if self.latitude is not None else None,
            'longitude': float(self.longitude) if self.longitude is not None else None,
            'category': self.category.name if self.category else None
        }