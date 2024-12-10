# Event Management Application

A Flask-based event management application that allows users to create, edit, and delete events with file uploads and location suggestions.

## Features

- Create, edit, and delete events
- Upload images (JPG, PNG) and PDF files
- Location suggestions with automatic address completion
- Date and time scheduling
- Responsive design using Bootstrap

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

Note: If you encounter any permission issues, you can alternatively install packages using:
```bash
pip install --user -r requirements.txt
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
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

The application will be available at `http://localhost:5000`

## Project Structure

```
event_management_app_python3/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── forms.py
│   ├── routes.py
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── main.js
│   │   └── uploads/
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── create_event.html
│       └── edit_event.html
└── requirements.txt
```

## Common Issues and Solutions

### Externally Managed Environment Error
If you see an error about "externally-managed-environment", make sure you:
1. Have created and activated the virtual environment (`.venv`) before installing packages
2. Have installed python3-venv package
3. Are not using the system Python installation

### Database Initialization Error
If you see an error about "Working outside of application context", make sure you:
1. Import both app and db: `from app import app, db`
2. Use an application context: `with app.app_context(): db.create_all()`

### Permission Issues
If you encounter permission issues:
1. Make sure you're using a virtual environment
2. Use `--user` flag with pip if needed
3. Ensure the uploads directory has correct permissions

## Usage

1. Visit the homepage to see all events
2. Click "Create New Event" to add an event
3. Fill in the event details:
   - Title (required)
   - Description (optional)
   - Start date and time (required)
   - End date and time (required)
   - Location details (optional)
   - Upload a file (optional)
4. Use the location input fields to get address suggestions
5. Edit or delete events from the homepage

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)