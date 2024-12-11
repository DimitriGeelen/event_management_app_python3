from app import app, db
from app.models import Category, Event
from datetime import datetime, timedelta

def create_sample_data():
    # Create sample categories
    categories = [
        {'name': 'Conference', 'description': 'Professional gatherings and conferences'},
        {'name': 'Workshop', 'description': 'Hands-on learning sessions'},
        {'name': 'Meetup', 'description': 'Informal community gatherings'},
        {'name': 'Concert', 'description': 'Music and performance events'},
        {'name': 'Exhibition', 'description': 'Art and cultural exhibitions'},
        {'name': 'Sport', 'description': 'Sports and fitness events'},
    ]

    # Create sample events data
    events = [
        {
            'title': 'Python Developers Conference',
            'description': 'Annual conference for Python developers featuring workshops and networking',
            'category': 'Conference',
            'location_name': 'Amsterdam Convention Center',
            'street_name': 'Europaplein',
            'street_number': '24',
            'postal_code': '1078 GZ',
            'start_offset': 5,  # days from now
            'duration': 2,  # days
            'latitude': 52.3423,
            'longitude': 4.8898
        },
        {
            'title': 'Web Development Workshop',
            'description': 'Learn the latest web development technologies and frameworks',
            'category': 'Workshop',
            'location_name': 'Rotterdam Tech Hub',
            'street_name': 'Westersingel',
            'street_number': '12',
            'postal_code': '3014 GN',
            'start_offset': 3,
            'duration': 1,
            'latitude': 51.9225,
            'longitude': 4.4792
        },
        {
            'title': 'Tech Meetup Netherlands',
            'description': 'Monthly meetup for tech enthusiasts and professionals',
            'category': 'Meetup',
            'location_name': 'Utrecht Science Park',
            'street_name': 'Heidelberglaan',
            'street_number': '8',
            'postal_code': '3584 CS',
            'start_offset': 7,
            'duration': 0.25,  # 6 hours
            'latitude': 52.0853,
            'longitude': 5.1779
        },
        {
            'title': 'Classical Music Evening',
            'description': 'An evening of classical masterpieces',
            'category': 'Concert',
            'location_name': 'Concertgebouw',
            'street_name': 'Concertgebouwplein',
            'street_number': '10',
            'postal_code': '1071 LN',
            'start_offset': 10,
            'duration': 0.125,  # 3 hours
            'latitude': 52.3564,
            'longitude': 4.8790
        },
        {
            'title': 'Modern Art Exhibition',
            'description': 'Contemporary art exhibition featuring local artists',
            'category': 'Exhibition',
            'location_name': 'Groningen Museum',
            'street_name': 'Museumeiland',
            'street_number': '1',
            'postal_code': '9711 ME',
            'start_offset': 1,
            'duration': 30,  # 30 days exhibition
            'latitude': 53.2127,
            'longitude': 6.5656
        },
        {
            'title': 'Marathon Rotterdam',
            'description': 'Annual Rotterdam Marathon event',
            'category': 'Sport',
            'location_name': 'Rotterdam Centrum',
            'street_name': 'Coolsingel',
            'street_number': '40',
            'postal_code': '3011 AD',
            'start_offset': 15,
            'duration': 0.5,  # 12 hours
            'latitude': 51.9244,
            'longitude': 4.4777
        },
    ]

    with app.app_context():
        print("Clearing existing data...")
        Event.query.delete()
        Category.query.delete()
        db.session.commit()

        print("Creating categories...")
        category_objects = {}
        for cat_data in categories:
            category = Category(name=cat_data['name'], description=cat_data['description'])
            db.session.add(category)
            category_objects[cat_data['name']] = category

        print("Creating events...")
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        
        for event_data in events:
            start_time = now + timedelta(days=event_data['start_offset'])
            end_time = start_time + timedelta(days=event_data['duration'])
            
            event = Event(
                title=event_data['title'],
                description=event_data['description'],
                category=category_objects[event_data['category']],
                location_name=event_data['location_name'],
                street_name=event_data['street_name'],
                street_number=event_data['street_number'],
                postal_code=event_data['postal_code'],
                start_datetime=start_time,
                end_datetime=end_time,
                latitude=event_data['latitude'],
                longitude=event_data['longitude']
            )
            db.session.add(event)

        print("Committing changes...")
        db.session.commit()
        print("Sample data created successfully!")

if __name__ == '__main__':
    create_sample_data()
