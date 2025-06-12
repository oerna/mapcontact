# Initialize database with tables and default admin user
from app import app, db, User

with app.app_context():
    # Create tables
    db.create_all()
    
    # Update admin user password
    admin = User.query.filter_by(username='admin').first()
    if admin:
        admin.set_password('McW3e4R5!')
        db.session.commit()
        print("Admin password has been reset")
    else:
        admin = User(username='admin')
        admin.set_password('McW3e4R5!')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created with new password")
    
    print("Database initialization completed")

if __name__ == '__main__':
    init_db() 