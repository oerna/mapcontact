import os
import sys
from app import app, db

def test_setup():
    print("Testing application setup...")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    try:
        # Test database connection
        with app.app_context():
            db.engine.connect()
            print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        raise

if __name__ == '__main__':
    test_setup() 