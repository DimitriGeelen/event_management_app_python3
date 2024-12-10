from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
db = SQLAlchemy(app)

from app import routes, models