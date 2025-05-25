import csv
import os
from app import db, Contact, User
from flask import Flask
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def import_contacts_from_csv(filename):
    if not os.path.exists(filename):
        print(f"Error: File {filename} not found")
        return

    # Initialize geocoder (in case we need to re-geocode addresses)
    geocoder = Nominatim(user_agent="mapcontacts")

    # Read from CSV and import to database
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        imported_count = 0
        skipped_count = 0

        for row in reader:
            # Check if contact with same name and address already exists
            existing_contact = Contact.query.filter_by(
                name=row['name'],
                address=row['address']
            ).first()

            if existing_contact:
                print(f"Skipping duplicate contact: {row['name']}")
                skipped_count += 1
                continue

            try:
                # Create new contact
                new_contact = Contact(
                    name=row['name'],
                    company=row['company'],
                    email=row['email'],
                    telephone=row['telephone'],
                    address=row['address'],
                    latitude=float(row['latitude']) if row['latitude'] else None,
                    longitude=float(row['longitude']) if row['longitude'] else None,
                    user_id=int(row['user_id'])
                )

                # If coordinates are missing, try to geocode the address
                if not new_contact.latitude or not new_contact.longitude:
                    try:
                        location = geocoder.geocode(row['address'])
                        if location:
                            new_contact.latitude = location.latitude
                            new_contact.longitude = location.longitude
                        else:
                            print(f"Could not geocode address for: {row['name']}")
                            continue
                    except GeocoderTimedOut:
                        print(f"Geocoding timed out for: {row['name']}")
                        continue

                db.session.add(new_contact)
                imported_count += 1
                
                # Commit every 10 records to avoid large transactions
                if imported_count % 10 == 0:
                    db.session.commit()
                    print(f"Imported {imported_count} contacts so far...")

            except Exception as e:
                print(f"Error importing contact {row['name']}: {str(e)}")
                continue

        # Final commit for remaining records
        db.session.commit()
        print(f"\nImport completed:")
        print(f"Successfully imported: {imported_count} contacts")
        print(f"Skipped duplicates: {skipped_count} contacts")

if __name__ == '__main__':
    app = Flask(__name__)
    # Use the same database configuration as in app.py
    instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance'))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "contacts.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the app context
    with app.app_context():
        # You can specify the CSV file to import
        import_file = input("Enter the path to the CSV file to import: ")
        import_contacts_from_csv(import_file) 