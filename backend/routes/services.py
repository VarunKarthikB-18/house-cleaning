from flask import Blueprint, jsonify
from models import ServiceType

services_bp = Blueprint('services', __name__)


@services_bp.route('/services', methods=['GET'])
def list_services():
    """Return all service types."""
    services = ServiceType.query.all()
    return jsonify({'services': [s.to_dict() for s in services]}), 200
