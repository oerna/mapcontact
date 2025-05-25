from app import app, db, User

new_password = "Cbg67&uJ2!"  # New admin password

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        admin.set_password(new_password)
        db.session.commit()
        print("Admin password has been reset!")
    else:
        print("Admin user not found.") 