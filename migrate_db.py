from app import app, db
from app import Contact
from sqlalchemy import text

def migrate_database():
    with app.app_context():
        # Add contact_type column to contacts table
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE contact ADD COLUMN contact_type VARCHAR(50);'))
            conn.commit()
        print("Successfully added contact_type column to contacts table")

def update_existing_contact_types():
    with app.app_context():
        allowed_types = ['Place', 'Artist', 'Booker', 'Festival', 'Other']
        updated = db.session.query(Contact).filter(~Contact.contact_type.in_(allowed_types) | (Contact.contact_type == None)).update({'contact_type': 'Other'}, synchronize_session=False)
        db.session.commit()
        print(f"Updated {updated} contacts to contact_type='Other' where not in allowed types or NULL.")

if __name__ == '__main__':
    # Only run the update for existing contact types to avoid duplicate column error
    update_existing_contact_types() 