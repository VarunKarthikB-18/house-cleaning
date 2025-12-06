from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
import json

# Database models for the house cleaning booking application
# Each model includes a to_dict() method for JSON serialization

class User(db.Model):
    """User model: stores customer and admin account information"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    address = db.Column(db.String(255))
    role = db.Column(db.String(20), default='user')  # 'user', 'admin', or 'cleaner'
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        """Hash and store password securely"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user object to dictionary for JSON response"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class ServiceType(db.Model):
    """ServiceType model: defines cleaning service packages (Basic, Standard, Deep, etc.)"""
    __tablename__ = 'service_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    duration_mins = db.Column(db.Integer, nullable=False)  # Service duration in minutes
    price = db.Column(db.Float, nullable=False)  # Base price for the service
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)  # Whether service is available

    def to_dict(self):
        """Convert service type to dictionary"""
        result = {
            'id': self.id,
            'name': self.name,
            'duration_mins': self.duration_mins,
            'price': self.price,
            'description': self.description,
        }
        # Handle active column - may not exist in older databases
        try:
            result['active'] = self.active
        except AttributeError:
            result['active'] = True  # Default to active if column doesn't exist
        return result

class Cleaner(db.Model):
    """Cleaner model: stores information about cleaning staff"""
    __tablename__ = 'cleaners'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50))
    active = db.Column(db.Boolean, default=True)  # Whether cleaner is available

    def to_dict(self):
        """Convert cleaner to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'active': self.active,
        }

class Booking(db.Model):
    """Booking model: stores appointment information including service, time, and customer details"""
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service_types.id'), nullable=False)
    cleaner_id = db.Column(db.Integer, db.ForeignKey('cleaners.id'), nullable=True)
    start_datetime = db.Column(db.DateTime(timezone=True), nullable=False)
    end_datetime = db.Column(db.DateTime(timezone=True), nullable=False)
    status = db.Column(db.String(30), default='pending')  # pending, confirmed, in_progress, completed, cancelled
    areas = db.Column(db.Text)  # JSON array of selected areas: ["Bathroom", "Kitchen", ...]
    payment_method = db.Column(db.String(20), default='cash')  # 'cash', 'cod', or 'online'
    price_total = db.Column(db.Float, nullable=False)  # Total price including extras
    address = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships for easy access to related objects
    user = db.relationship('User', backref=db.backref('bookings', lazy=True))
    service = db.relationship('ServiceType')
    cleaner = db.relationship('Cleaner')

    def set_areas(self, areas_list):
        """Store areas as JSON string"""
        self.areas = json.dumps(areas_list) if areas_list else '[]'

    def get_areas(self):
        """Retrieve areas as Python list"""
        return json.loads(self.areas) if self.areas else []

    def to_dict(self):
        """Convert booking to dictionary with nested relationships"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'service_id': self.service_id,
            'service': self.service.to_dict() if self.service else None,
            'cleaner_id': self.cleaner_id,
            'cleaner': self.cleaner.to_dict() if self.cleaner else None,
            'start_datetime': self.start_datetime.isoformat() if self.start_datetime else None,
            'end_datetime': self.end_datetime.isoformat() if self.end_datetime else None,
            'status': self.status,
            'areas': self.get_areas(),
            'payment_method': self.payment_method,
            'price_total': self.price_total,
            'address': self.address,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class Review(db.Model):
    """Review model: stores customer reviews for completed bookings"""
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False, unique=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 star rating
    comment = db.Column(db.Text)
    moderated = db.Column(db.Boolean, default=False)  # Admin approval flag
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))
    booking = db.relationship('Booking', backref=db.backref('review', uselist=False))

    def to_dict(self):
        """Convert review to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'booking_id': self.booking_id,
            'booking': self.booking.to_dict() if self.booking else None,
            'rating': self.rating,
            'comment': self.comment,
            'moderated': self.moderated,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
