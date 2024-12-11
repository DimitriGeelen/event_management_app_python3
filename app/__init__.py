from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    load_dotenv()
    
    # Get the absolute path of the app directory
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    # Set the database path to be in the instance folder
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "events.db")}'
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    print(f"Upload directory: {app.config['UPLOAD_FOLDER']}")
    print(f"Database path: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    from app import routes
    app.register_blueprint(routes.bp)
    
    return app

# Create the application instance
app = create_app()