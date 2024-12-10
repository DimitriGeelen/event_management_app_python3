from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    events = db.relationship('Event', backref='creator', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

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
    
    # New fields
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50))
    is_public = db.Column(db.Boolean, default=True)
    max_participants = db.Column(db.Integer)
    current_participants = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')  # active, cancelled, completed
    participants = db.relationship('EventParticipant', backref='event', lazy='dynamic')

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
            'creator': self.creator.username,
            'category': self.category,
            'is_public': self.is_public,
            'max_participants': self.max_participants,
            'current_participants': self.current_participants,
            'status': self.status
        }

class EventParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='registered')  # registered, cancelled, attended
    
    user = db.relationship('User', backref=db.backref('event_participations', lazy='dynamic'))

    def __repr__(self):
        return f'<EventParticipant {self.user.username} - Event {self.event_id}>'