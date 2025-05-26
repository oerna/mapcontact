from app import app, db, User
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('change-this-password')  # Change this password immediately after first login
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created")
        else:
            print("Admin user already exists")

if __name__ == '__main__':
    init_db()
    print("Database initialization completed") 