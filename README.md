# MapContacts

A Flask-based contact management application with geolocation features.

## Project Structure

```
mapcontacts/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   └── utils.py
├── config/
│   ├── __init__.py
│   ├── development.py
│   └── production.py
├── instance/
├── logs/
├── static/
├── templates/
├── .env.example
├── .gitignore
├── config.py
├── requirements.txt
└── run.py
```

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd mapcontacts
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```bash
cp .env.example .env
```
Edit the `.env` file with your configuration settings.

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:
```bash
python run.py
```

## Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and modify the values as needed:

- `FLASK_APP`: The application entry point
- `FLASK_ENV`: Development or production environment
- `SECRET_KEY`: Application secret key
- `DATABASE_URL`: Database connection URL
- `PERMANENT_SESSION_LIFETIME`: Session lifetime in seconds

## Development

For development, set:
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
```

## Production

For production deployment:
1. Set appropriate environment variables
2. Use a production-grade WSGI server (e.g., Gunicorn)
3. Set up a reverse proxy (e.g., Nginx)
4. Configure SSL/TLS

## Database

The application uses SQLAlchemy with MySQL. Make sure to:
1. Create a MySQL database
2. Set the correct DATABASE_URL in your .env file
3. Run database migrations

## Security Notes

- Change the default admin password after first login
- Use strong passwords
- Keep your .env file secure and never commit it to version control
- Regularly update dependencies 