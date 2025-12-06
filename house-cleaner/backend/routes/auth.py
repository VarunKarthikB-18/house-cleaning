from flask import Blueprint, request, jsonify
from extensions import db, jwt
from models import User
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user. Expects JSON with email and password (minimum 6 characters).
    Optional fields: name, phone, address.
    """
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'success': False, 'msg': 'Email and password required', 'code': 400}), 400
    
    if len(password) < 6:
        return jsonify({'success': False, 'msg': 'Password must be at least 6 characters', 'code': 400}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'msg': 'Email already registered', 'code': 400}), 400

    user = User(
        email=email,
        name=data.get('name'),
        phone=data.get('phone'),
        address=data.get('address')
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'success': True, 'data': user.to_dict(), 'msg': 'User registered'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login route. Returns JWT access token and basic user info.
    Token includes identity payload with user_id and role.
    """
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'success': False, 'msg': 'Email and password required', 'code': 400}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'msg': 'Invalid credentials', 'code': 401}), 401

    identity = {'user_id': user.id, 'role': user.role}
    token = create_access_token(identity=identity)
    return jsonify({
        'success': True,
        'access_token': token,
        'data': user.to_dict(),
        'msg': 'Login successful'
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Return the current logged-in user's profile."""
    identity = get_jwt_identity() or {}
    user_id = identity.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'msg': 'Unauthorized', 'code': 401}), 401
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'msg': 'User not found', 'code': 404}), 404
    return jsonify({'success': True, 'data': user.to_dict()}), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user's profile (name, phone, address)."""
    identity = get_jwt_identity() or {}
    user_id = identity.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'msg': 'Unauthorized', 'code': 401}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'msg': 'User not found', 'code': 404}), 404
    
    data = request.get_json() or {}
    if 'name' in data:
        user.name = data['name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'address' in data:
        user.address = data['address']
    
    db.session.commit()
    return jsonify({'success': True, 'data': user.to_dict(), 'msg': 'Profile updated'}), 200
