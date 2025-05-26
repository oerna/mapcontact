from setuptools import setup
import os
import subprocess
import sys

def setup_environment():
    # Create logs directory
    try:
        os.makedirs('logs')
    except OSError:
        if not os.path.isdir('logs'):
            raise
    
    # Install requirements using the system pip
    print("Installing requirements...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-e', '.'])
    
    print("Setup completed successfully!")

if __name__ == '__main__':
    setup_environment()

setup(
    name='mapcontacts',
    version='1.0',
    install_requires=[
        'Flask==3.0.0',
        'Flask-SQLAlchemy==3.1.1',
        'python-dotenv==1.0.0',
        'geopy==2.4.1',
        'Flask-CORS==4.0.0',
        'Flask-Login==0.6.3',
        'Werkzeug==3.0.1',
        'psycopg2-binary==2.9.9'
    ],
    python_requires='>=3.9',
) 