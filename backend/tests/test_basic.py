import pytest
from app import create_app
from config import TestingConfig
from extensions import db
import json
from models import User, ServiceType


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        # seed minimal data
        s = ServiceType(name='Test Service', duration_mins=60, price=10.0, description='Test')
        db.session.add(s)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


def test_register_login_and_booking(client):
    # register
    rv = client.post('/auth/register', json={'email': 'tuser@example.com', 'password': 'pass123'})
    assert rv.status_code == 201

    # login
    rv = client.post('/auth/login', json={'email': 'tuser@example.com', 'password': 'pass123'})
    assert rv.status_code == 200
    data = rv.get_json()
    token = data['access_token']

    # create booking
    # choose a date 1 day from now
    from datetime import datetime, timedelta
    start = (datetime.now() + timedelta(days=1, hours=2)).isoformat()
    rv = client.post('/bookings', json={'service_id': 1, 'start_datetime': start, 'address': 'x'}, headers={'Authorization': f'Bearer {token}'})
    assert rv.status_code == 201

    # list bookings
    rv = client.get('/bookings', headers={'Authorization': f'Bearer {token}'})
    data = rv.get_json()
    assert 'bookings' in data
    assert len(data['bookings']) >= 1
