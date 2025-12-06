"""
Seed script to create sample data: service packages, admin user, test users, cleaners, bookings, and reviews.
Run with: python seeds.py
"""
from app import create_app
from config import Config
from extensions import db
from models import User, ServiceType, Cleaner, Booking, Review
from datetime import datetime, timezone, timedelta


def calculate_price_total(service_price, areas_count):
    """Calculate total price: base + area extras + tax"""
    base_price = service_price
    area_extra = max(0, (areas_count - 1) * 10)  # First area included
    subtotal = base_price + area_extra
    tax = subtotal * 0.08
    return round(subtotal + tax, 2)


def run():
    app = create_app()
    with app.app_context():
        db.create_all()

        print("Creating service types...")
        # Create 5-6 service packages as specified
        services_data = [
            {
                'name': 'Basic Clean (30m)',
                'duration_mins': 30,
                'price': 35.0,
                'description': 'Quick tidy-up for small spaces. Perfect for studios or single rooms.',
                'active': True
            },
            {
                'name': 'Standard Clean (60m)',
                'duration_mins': 60,
                'price': 65.0,
                'description': 'Thorough cleaning for apartments and small homes. Includes dusting, vacuuming, and bathroom cleaning.',
                'active': True
            },
            {
                'name': 'Deep Clean (120m)',
                'duration_mins': 120,
                'price': 140.0,
                'description': 'Comprehensive deep cleaning. Includes inside cabinets, baseboards, and detailed sanitization.',
                'active': True
            },
            {
                'name': 'Move-Out Clean',
                'duration_mins': 180,
                'price': 200.0,
                'description': 'Complete cleaning for move-out inspection. Includes inside appliances, closets, and all areas.',
                'active': True
            },
            {
                'name': 'Post-Party Clean',
                'duration_mins': 90,
                'price': 110.0,
                'description': 'Specialized cleaning after events. Focus on high-traffic areas and kitchen cleanup.',
                'active': True
            },
            {
                'name': 'Premium Clean (180m)',
                'duration_mins': 180,
                'price': 250.0,
                'description': 'Premium service with attention to detail. Includes windows, inside appliances, and deep sanitization.',
                'active': True
            },
        ]

        # Only create services if they don't exist
        if ServiceType.query.count() == 0:
            for service_info in services_data:
                service = ServiceType(**service_info)
                db.session.add(service)
            db.session.commit()
            print(f"Created {len(services_data)} service types")

        print("Creating admin user...")
        # Admin user
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(
                email='admin@example.com',
                name='Admin User',
                phone='555-0000',
                address='123 Admin St',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: admin@example.com / admin123")

        print("Creating test users...")
        # Test users
        test_users_data = [
            {
                'email': 'user@example.com',
                'name': 'Demo User',
                'phone': '555-0001',
                'address': '456 Main St, City, State',
                'password': 'user123'
            },
            {
                'email': 'john@example.com',
                'name': 'John Doe',
                'phone': '555-0002',
                'address': '789 Oak Ave, City, State',
                'password': 'john123'
            },
        ]

        for user_data in test_users_data:
            if not User.query.filter_by(email=user_data['email']).first():
                user = User(
                    email=user_data['email'],
                    name=user_data['name'],
                    phone=user_data['phone'],
                    address=user_data['address'],
                    role='user'
                )
                user.set_password(user_data['password'])
                db.session.add(user)
        db.session.commit()
        print(f"Created {len(test_users_data)} test users")

        print("Creating cleaners...")
        # Cleaners
        cleaners_data = [
            {'name': 'Maria Garcia', 'phone': '555-1001', 'active': True},
            {'name': 'James Wilson', 'phone': '555-1002', 'active': True},
            {'name': 'Sarah Johnson', 'phone': '555-1003', 'active': True},
        ]

        if Cleaner.query.count() == 0:
            for cleaner_data in cleaners_data:
                cleaner = Cleaner(**cleaner_data)
                db.session.add(cleaner)
            db.session.commit()
            print(f"Created {len(cleaners_data)} cleaners")

        print("Creating sample bookings...")
        # Sample bookings
        if Booking.query.count() == 0:
            user = User.query.filter_by(email='user@example.com').first()
            john = User.query.filter_by(email='john@example.com').first()
            service_basic = ServiceType.query.filter_by(name='Basic Clean (30m)').first()
            service_standard = ServiceType.query.filter_by(name='Standard Clean (60m)').first()
            service_deep = ServiceType.query.filter_by(name='Deep Clean (120m)').first()
            cleaner1 = Cleaner.query.first()

            now = datetime.now(timezone.utc)

            # Pending booking
            start1 = now + timedelta(days=2, hours=4)
            areas1 = ['Bathroom', 'Kitchen', 'Living Room']
            booking1 = Booking(
                user_id=user.id,
                service_id=service_standard.id,
                start_datetime=start1,
                end_datetime=start1 + timedelta(minutes=service_standard.duration_mins),
                address=user.address,
                notes='Please use eco-friendly products',
                payment_method='cash',
                status='pending'
            )
            booking1.set_areas(areas1)
            booking1.price_total = calculate_price_total(service_standard.price, len(areas1))
            db.session.add(booking1)

            # Confirmed booking
            start2 = now + timedelta(days=3, hours=2)
            areas2 = ['Bathroom', 'Kitchen']
            booking2 = Booking(
                user_id=john.id,
                service_id=service_basic.id,
                cleaner_id=cleaner1.id,
                start_datetime=start2,
                end_datetime=start2 + timedelta(minutes=service_basic.duration_mins),
                address=john.address,
                notes='Gate code: 1234',
                payment_method='cod',
                status='confirmed'
            )
            booking2.set_areas(areas2)
            booking2.price_total = calculate_price_total(service_basic.price, len(areas2))
            db.session.add(booking2)

            # Completed booking (for reviews)
            start3 = now - timedelta(days=2, hours=5)
            areas3 = ['Bathroom', 'Kitchen', 'Living Room', 'Bedroom']
            booking3 = Booking(
                user_id=user.id,
                service_id=service_deep.id,
                cleaner_id=cleaner1.id,
                start_datetime=start3,
                end_datetime=start3 + timedelta(minutes=service_deep.duration_mins),
                address=user.address,
                payment_method='cash',
                status='completed'
            )
            booking3.set_areas(areas3)
            booking3.price_total = calculate_price_total(service_deep.price, len(areas3))
            db.session.add(booking3)

            db.session.commit()
            print("Created 3 sample bookings")

            print("Creating sample reviews...")
            # Sample review for completed booking
            review = Review(
                user_id=user.id,
                booking_id=booking3.id,
                rating=5,
                comment='Excellent service! Very thorough and professional. Highly recommend!',
                moderated=True
            )
            db.session.add(review)
            db.session.commit()
            print("Created 1 sample review")

        print('\n✅ Seeding complete!')
        print('\nLogin credentials:')
        print('  Admin: admin@example.com / admin123')
        print('  User:  user@example.com / user123')
        print('  User:  john@example.com / john123')


if __name__ == '__main__':
    run()
