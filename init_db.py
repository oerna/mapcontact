from app import app, db, User

with app.app_context():
    db.create_all()
    # Create default admin user if it doesn't exist
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('change-this-password')  # Change this password immediately after first login
        db.session.add(admin)
        db.session.commit()
        print("Database initialized with admin user") 