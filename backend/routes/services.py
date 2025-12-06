from flask import Blueprint, request, jsonify
from models import ServiceType
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db

services_bp = Blueprint('services', __name__)


def admin_only(identity):
    """Helper function to check if user is admin"""
    return identity and identity.get('role') == 'admin'


@services_bp.route('/services', methods=['GET'])
def list_services():
    """Return all active service types. Public endpoint."""
    # Only show active services to non-admins
    identity = None
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
    except:
        # No token or invalid token - that's okay for public endpoint
        pass
    
    is_admin = admin_only(identity) if identity else False
    
    # Check if active column exists by inspecting the model
    has_active_column = hasattr(ServiceType, 'active')
    
    try:
        if is_admin:
            services = ServiceType.query.order_by(ServiceType.name).all()
        elif has_active_column:
            # Try to filter by active, but fallback to all if it fails
            try:
                services = ServiceType.query.filter_by(active=True).order_by(ServiceType.name).all()
            except Exception:
                # If query fails (column might not exist in DB), show all
                services = ServiceType.query.order_by(ServiceType.name).all()
        else:
            # If active column doesn't exist in model, show all services
            services = ServiceType.query.order_by(ServiceType.name).all()
    except Exception as e:
        # Fallback: show all services if any error occurs
        services = ServiceType.query.order_by(ServiceType.name).all()
    
    return jsonify({'success': True, 'data': [s.to_dict() for s in services]}), 200


@services_bp.route('/services', methods=['POST'])
@jwt_required()
def create_service():
    """Create a new service type. Admin only."""
    identity = get_jwt_identity()
    if not admin_only(identity):
        return jsonify({'success': False, 'msg': 'Admin access required', 'code': 403}), 403
    
    data = request.get_json() or {}
    name = data.get('name')
    duration_mins = data.get('duration_mins')
    price = data.get('price')
    
    if not name or not duration_mins or not price:
        return jsonify({'success': False, 'msg': 'name, duration_mins, and price required', 'code': 400}), 400
    
    service = ServiceType(
        name=name,
        duration_mins=duration_mins,
        price=price,
        description=data.get('description', ''),
        active=data.get('active', True)
    )
    db.session.add(service)
    db.session.commit()
    
    return jsonify({'success': True, 'data': service.to_dict(), 'msg': 'Service created'}), 201


@services_bp.route('/services/<int:service_id>', methods=['PUT'])
@jwt_required()
def update_service(service_id):
    """Update a service type. Admin only."""
    identity = get_jwt_identity()
    if not admin_only(identity):
        return jsonify({'success': False, 'msg': 'Admin access required', 'code': 403}), 403
    
    service = ServiceType.query.get_or_404(service_id)
    data = request.get_json() or {}
    
    if 'name' in data:
        service.name = data['name']
    if 'duration_mins' in data:
        service.duration_mins = data['duration_mins']
    if 'price' in data:
        service.price = data['price']
    if 'description' in data:
        service.description = data['description']
    if 'active' in data:
        service.active = data['active']
    
    db.session.commit()
    return jsonify({'success': True, 'data': service.to_dict(), 'msg': 'Service updated'}), 200


@services_bp.route('/services/<int:service_id>', methods=['DELETE'])
@jwt_required()
def delete_service(service_id):
    """Delete a service type. Admin only."""
    identity = get_jwt_identity()
    if not admin_only(identity):
        return jsonify({'success': False, 'msg': 'Admin access required', 'code': 403}), 403
    
    service = ServiceType.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    
    return jsonify({'success': True, 'msg': 'Service deleted'}), 200
