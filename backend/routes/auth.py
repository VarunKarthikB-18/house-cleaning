from flask import Blueprint, request, jsonify
from extensions import db, jwt
from models import User
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user. Expects JSON with email and password."""
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'msg': 'Email and password required', 'code': 400}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'msg': 'Email already registered', 'code': 400}), 400

    user = User(email=email, name=data.get('name'), phone=data.get('phone'), address=data.get('address'))
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'msg': 'User registered', 'user': user.to_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login route. Returns JWT access token and basic user info."""
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'msg': 'Email and password required', 'code': 400}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'msg': 'Invalid credentials', 'code': 401}), 401

    identity = {'user_id': user.id, 'role': user.role}
    token = create_access_token(identity=identity)
    return jsonify({'access_token': token, 'user': user.to_dict()}), 200
