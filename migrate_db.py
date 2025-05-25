from app import app, db
from sqlalchemy import text

def migrate_database():
    with app.app_context():
        # Add notes column to contacts table
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE contact ADD COLUMN notes TEXT;'))
            conn.commit()
        print("Successfully added notes column to contacts table")

if __name__ == '__main__':
    migrate_database() 