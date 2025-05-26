from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Check if admin user exists
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print("Admin user exists")
        # Reset admin password to 'admin123'
        admin.set_password('admin123')
        db.session.commit()
        print("Admin password has been reset to 'admin123'")
    else:
        print("Creating admin user")
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created with password 'admin123'") 