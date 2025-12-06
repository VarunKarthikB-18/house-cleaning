import pytest
from app import create_app
from config import TestingConfig
from extensions import db

@pytest.fixture
def app():
    """Create test app with in-memory database."""
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()
