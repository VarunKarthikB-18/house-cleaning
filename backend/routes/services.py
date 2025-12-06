from flask import Blueprint, jsonify
from models import ServiceType
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User

services_bp = Blueprint('services', __name__)


@services_bp.route('/services', methods=['GET'])
def list_services():
    """Return all service types."""
    services = ServiceType.query.all()
    return jsonify({'services': [s.to_dict() for s in services]}), 200


@services_bp.route('/user/profile', methods=['GET'])
@jwt_required()
def user_profile():
    """Return the profile for the currently authenticated user."""
    identity = get_jwt_identity() or {}
    user_id = identity.get('user_id')
    if not user_id:
        return jsonify({'msg': 'Unauthorized', 'code': 401}), 401
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'User not found', 'code': 404}), 404
    return jsonify(user.to_dict()), 200
