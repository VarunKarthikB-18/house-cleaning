"""
Basic integration tests for the house cleaning booking application.
Tests user registration, login, and booking creation flow.
"""
import pytest
from app import create_app
from config import TestingConfig
from extensions import db
import json
from models import User, ServiceType
from datetime import datetime, timedelta, timezone


@pytest.fixture
def app():
    """Create test app with test database"""
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        # Seed minimal test data
        s = ServiceType(
            name='Test Service',
            duration_mins=60,
            price=50.0,
            description='Test service for unit tests',
            active=True
        )
        db.session.add(s)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


def test_register_login_and_booking(client):
    """
    Test complete flow: register user, login, create booking, and verify booking exists.
    This is the main integration test that validates the core booking functionality.
    """
    # Register a new user
    rv = client.post('/auth/register', json={
        'email': 'tuser@example.com',
        'password': 'pass123',
        'name': 'Test User',
        'phone': '555-1234',
        'address': '123 Test St'
    })
    assert rv.status_code == 201
    data = rv.get_json()
    assert data['success'] is True
    assert data['data']['email'] == 'tuser@example.com'

    # Login with registered credentials
    rv = client.post('/auth/login', json={
        'email': 'tuser@example.com',
        'password': 'pass123'
    })
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['success'] is True
    assert 'access_token' in data
    token = data['access_token']
    assert token is not None

    # Create a booking with future datetime (minimum 3 hours lead time)
    # Use UTC-aware datetime for consistency
    future_time = datetime.now(timezone.utc) + timedelta(days=1, hours=4)
    start_iso = future_time.isoformat()

    rv = client.post('/bookings', json={
        'service_id': 1,
        'start_datetime': start_iso,
        'address': '123 Test Street, Test City',
        'areas': ['Bathroom', 'Kitchen'],
        'payment_method': 'cash',
        'notes': 'Test booking notes'
    }, headers={'Authorization': f'Bearer {token}'})
    
    assert rv.status_code == 201
    booking_data = rv.get_json()
    assert booking_data['success'] is True
    assert 'data' in booking_data
    assert booking_data['data']['status'] == 'pending'
    assert booking_data['data']['payment_method'] == 'cash'
    assert 'areas' in booking_data['data']
    assert len(booking_data['data']['areas']) == 2

    # List bookings to verify the created booking exists
    rv = client.get('/bookings', headers={'Authorization': f'Bearer {token}'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['success'] is True
    assert 'data' in data
    assert len(data['data']) >= 1
    
    # Verify the booking we created is in the list
    bookings = data['data']
    found_booking = None
    for booking in bookings:
        if booking['address'] == '123 Test Street, Test City':
            found_booking = booking
            break
    
    assert found_booking is not None
    assert found_booking['status'] == 'pending'
