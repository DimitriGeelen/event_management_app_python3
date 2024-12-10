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
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
... 
>>> exit()
```

7. Run the application:
```bash
# Method 1: Using Flask CLI (LAN access)
export FLASK_APP=run.py
export FLASK_ENV=development
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

## Project Structure

```
event_management_app_python3/
├── app/
│   ├── __init__.py      # Application factory and configuration
│   ├── models.py        # Database models
│   ├── forms.py         # Form definitions
│   ├── routes.py        # Route handlers and business logic
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── main.js
│   │   └── uploads/     # Uploaded files directory
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── create_event.html
│       └── edit_event.html
├── requirements.txt     # Python dependencies
└── run.py              # Application entry point
```

## Security Considerations for LAN Access

1. The application is set to be accessible on your local network. Be aware that:
   - Anyone on your network can access the application
   - Debug mode is enabled for development (disable for production)
   - Consider adding authentication for sensitive environments

2. For production use, consider:
   - Adding user authentication
   - Using HTTPS
   - Configuring a proper web server (like nginx)
   - Disabling debug mode

## Common Issues and Solutions

### Externally Managed Environment Error
If you see an error about "externally-managed-environment", make sure you:
1. Have created and activated the virtual environment (`.venv`) before installing packages
2. Have installed python3-venv package
3. Are not using the system Python installation

### Database Initialization Error
If you see an error about "Working outside of application context", make sure you:
1. Import both create_app and db: `from app import create_app, db`
2. Create the app: `app = create_app()`
3. Use an application context: `with app.app_context(): db.create_all()`

### Network Access Issues
If others cannot access the application:
1. Verify the application is running with host='0.0.0.0'
2. Check your firewall settings: `sudo ufw status`
3. Allow port 5000 if needed: `sudo ufw allow 5000`
4. Ensure you're using the correct IP address

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