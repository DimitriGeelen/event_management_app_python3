# Event Management Application

A Flask-based event management application that allows users to create, edit, and delete events with file uploads and location suggestions.

## Features

- Create, edit, and delete events
- Upload images (JPG, PNG) and PDF files
- Location suggestions with automatic address completion
- Date and time scheduling
- Responsive design using Bootstrap
- LAN access support

## Requirements

- Python 3.8+
- Ubuntu 24.04
- Pip package manager

## Installation

1. Clone the repository:
```bash
git clone https://github.com/DimitriGeelen/event_management_app_python3.git
cd event_management_app_python3
```

2. First, install required system packages:
```bash
sudo apt update
sudo apt install python3-venv python3-pip
```

3. Create and prepare the virtual environment:
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip in the virtual environment
pip install --upgrade pip
```

4. Install dependencies (make sure your virtual environment is activated):
```bash
pip install -r requirements.txt
```

5. Create the necessary directories:
```bash
mkdir -p app/static/uploads
```

6. Initialize the database:
```python
python3
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
... 
>>> exit()
```

7. Run the application:
```bash
# Method 1: Using Flask CLI (LAN access)
export FLASK_APP=app
flask run --host=0.0.0.0

# Method 2: Using Python directly (recommended for LAN access)
python3 run.py
```

The application will be available at:
- Local access: `http://localhost:5000`
- LAN access: `http://<your-ip-address>:5000`

To find your IP address, use the command:
```bash
ip addr show
# or
hostname -I
```

[Rest of the README remains the same...]