from app import app, db
from app.models import Category, Event
from datetime import datetime, timedelta

def create_sample_data():
    print("Creating sample data...")
    
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
            'location_name': 'Amsterdam RAI',
            'street_name': 'Europaplein',
            'street_number': '24',
            'postal_code': '1078 GZ',
            'start_offset': 5,  # days from now
            'duration': 2,  # days
            'latitude': 52.3376,
            'longitude': 4.8900
        },
        {
            'title': 'Tech Meetup Rotterdam',
            'description': 'Monthly meetup for tech enthusiasts',
            'category': 'Meetup',
            'location_name': 'Rotterdam Central Library',
            'street_name': 'Hoogstraat',
            'street_number': '110',
            'postal_code': '3011 PV',
            'start_offset': 3,
            'duration': 0.25,  # 6 hours
            'latitude': 51.9244,
            'longitude': 4.4777
        },
        {
            'title': 'Utrecht Jazz Festival',
            'description': 'Annual jazz music festival',
            'category': 'Concert',
            'location_name': 'TivoliVredenburg',
            'street_name': 'Vredenburgkade',
            'street_number': '11',
            'postal_code': '3511 WC',
            'start_offset': 7,
            'duration': 3,
            'latitude': 52.0907,
            'longitude': 5.1140
        }
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

        # Print created events for verification
        print("\nCreated Events:")
        events = Event.query.all()
        for event in events:
            print(f"Event: {event.title}")
            print(f"Location: {event.location_name}, {event.street_name} {event.street_number}, {event.postal_code}")
            print(f"Coordinates: lat={event.latitude}, lon={event.longitude}\n")

if __name__ == '__main__':
    create_sample_data()