# Facial Feedback Application

A web application for collecting user feedback through facial emotion recognition.

## Features

- Real-time facial emotion detection
- User feedback collection
- Dashboard for feedback analysis
- Admin interface for managing feedback data

## Technology Stack

- Django 4.2+
- OpenCV for image processing
- TensorFlow for emotion recognition
- Bootstrap 4 for frontend
- SQLite for development database

## Setup Instructions

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Run development server:
```bash
python manage.py runserver
```

## Project Structure

The project follows a modular structure:
- `facial_feedback/` - Main project directory
- `emotion_feedback/` - Main application directory
- `templates/` - HTML templates
- `static/` - Static files (CSS, JS, images)
- `media/` - User uploaded files

## SCRUM Process

This project is managed using SCRUM methodology:
- Sprint duration: 2 weeks
- Daily standups
- Sprint planning and retrospective meetings
- Project board maintained on GitHub Projects

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. 