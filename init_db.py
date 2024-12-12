from app import app, db
from app.models import Category, Event

def init_db():
    print("Initializing database...")
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Database initialized!")

if __name__ == '__main__':
    init_db()
    print("\nNow you can run:")
    print("python3 sample_data.py")
