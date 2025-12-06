"""Seed script to create sample data: services, admin user, cleaner, and sample bookings."""
from app import create_app
from config import Config
from extensions import db
from models import User, ServiceType, Cleaner, Booking
from datetime import datetime, timezone, timedelta


def run():
    app = create_app()
    with app.app_context():
        db.create_all()

        # Create service types
        if not ServiceType.query.first():
            s1 = ServiceType(name='Standard Cleaning', duration_mins=60, price=50.0, description='Basic cleaning')
            s2 = ServiceType(name='Deep Cleaning', duration_mins=180, price=180.0, description='Deep cleaning')
            db.session.add_all([s1, s2])
            db.session.commit()

        # Admin user
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(email='admin@example.com', name='Admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

        # Cleaner
        if not Cleaner.query.first():
            cleaner = Cleaner(name='Sam Cleaner', phone='555-0001', active=True)
            db.session.add(cleaner)
            db.session.commit()

        # Sample booking
        if not Booking.query.first():
            user = User(email='user@example.com', name='Demo User')
            user.set_password('user123')
            db.session.add(user)
            db.session.commit()

            service = ServiceType.query.first()
            start = datetime.now(timezone.utc) + timedelta(days=1, hours=2)
            end = start + timedelta(minutes=service.duration_mins)
            booking = Booking(user_id=user.id, service_id=service.id, start_datetime=start, end_datetime=end,
                              address='123 Demo St', notes='Please bring eco products', status='pending')
            db.session.add(booking)
            db.session.commit()

        print('Seeding complete')


if __name__ == '__main__':
    run()
