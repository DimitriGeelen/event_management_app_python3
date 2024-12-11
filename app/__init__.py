from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_talisman import Talisman
from dotenv import load_dotenv
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    load_dotenv()
    
    # Basic Flask configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), "events.db")}'
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    print(f"Upload directory: {app.config['UPLOAD_FOLDER']}")
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configure Talisman (HTTPS)
    csp = {
        'default-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            'stackpath.bootstrapcdn.com',
            'cdn.jsdelivr.net',
            'cdnjs.cloudflare.com',
        ],
        'img-src': ['*', 'data:', '\'self\''],
        'script-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            '\'unsafe-eval\'',
            'cdn.jsdelivr.net',
            'cdnjs.cloudflare.com',
        ],
        'style-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            'cdn.jsdelivr.net',
            'cdnjs.cloudflare.com',
            'fonts.googleapis.com',
        ],
        'font-src': ['*', 'data:', '\'self\''],
    }
    
    Talisman(app,
             force_https=True,
             content_security_policy=csp,
             content_security_policy_nonce_in=['script-src'],
             feature_policy={
                 'geolocation': '\'self\''
             })
    
    from app import routes
    app.register_blueprint(routes.bp)
    
    return app

# Create the application instance
app = create_app()