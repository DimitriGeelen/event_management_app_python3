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

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create the necessary directories:
```bash
mkdir -p app/static/uploads
```

5. Initialize the database:
```bash
python3
>>> from app import db
>>> db.create_all()
>>> exit()
```

6. Run the application:
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