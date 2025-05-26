import csv
import os
from app import db, Contact, User
from flask import Flask
from datetime import datetime

def export_contacts_to_csv():
    # Ensure the exports directory exists
    if not os.path.exists('exports'):
        os.makedirs('exports')

    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'exports/contacts_export_{timestamp}.csv'

    # Get all contacts from the database
    contacts = Contact.query.all()

    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'company', 'email', 'telephone', 'address', 'latitude', 'longitude', 'user_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for contact in contacts:
            writer.writerow({
                'name': contact.name,
                'company': contact.company,
                'email': contact.email,
                'telephone': contact.telephone,
                'address': contact.address,
                'latitude': contact.latitude,
                'longitude': contact.longitude,
                'user_id': contact.user_id
            })
    
    print(f"Exported {len(contacts)} contacts to {filename}")
    return filename

if __name__ == '__main__':
    app = Flask(__name__)
    # Use the same database configuration as in app.py
    instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance'))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "contacts.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the app context
    with app.app_context():
        exported_file = export_contacts_to_csv() 