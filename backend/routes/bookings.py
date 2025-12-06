from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Booking, ServiceType, User, Cleaner
from datetime import datetime, timedelta, timezone

bookings_bp = Blueprint('bookings', __name__)


def parse_iso_to_utc(iso_str):
    """Parse ISO string to UTC-aware datetime. If no tzinfo, assume local then convert to UTC."""
    try:
        dt = datetime.fromisoformat(iso_str)
    except Exception:
        raise ValueError('Invalid datetime format')
    if dt.tzinfo is None:
        # assume local and convert to UTC
        dt = dt.astimezone(timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt


def business_hours_ok(start_utc, end_utc):
    # business hours enforced in UTC 08:00-19:00
    if start_utc.hour < 8 or end_utc.hour > 19 or (end_utc.hour == 19 and end_utc.minute > 0):
        return False
    return True


@bookings_bp.route('', methods=['POST'])
@jwt_required()
def create_booking():
    """Create a booking for logged-in user."""
    identity = get_jwt_identity()
    user_id = identity.get('user_id')
    data = request.get_json() or {}
    service_id = data.get('service_id')
    start_iso = data.get('start_datetime')
    address = data.get('address')
    notes = data.get('notes')

    if not service_id or not start_iso:
        return jsonify({'msg': 'service_id and start_datetime required', 'code': 400}), 400

    service = ServiceType.query.get(service_id)
    if not service:
        return jsonify({'msg': 'Service not found', 'code': 404}), 404

    try:
        start_dt = parse_iso_to_utc(start_iso)
    except ValueError:
        return jsonify({'msg': 'Invalid start_datetime', 'code': 400}), 400

    now_utc = datetime.now(timezone.utc)
    if start_dt < now_utc + timedelta(minutes=10):
        return jsonify({'msg': 'start_datetime must be at least 10 minutes in the future', 'code': 400}), 400

    end_dt = start_dt + timedelta(minutes=service.duration_mins)
    if not business_hours_ok(start_dt, end_dt):
        return jsonify({'msg': 'Booking must be within business hours (08:00-19:00 UTC)', 'code': 400}), 400

    booking = Booking(user_id=user_id, service_id=service.id, start_datetime=start_dt, end_datetime=end_dt,
                      address=address, notes=notes, status='pending')
    db.session.add(booking)
    db.session.commit()

    return jsonify({'msg': 'Booking created', 'booking': booking.to_dict()}), 201


@bookings_bp.route('', methods=['GET'])
@jwt_required()
def list_bookings():
    identity = get_jwt_identity()
    user_id = identity.get('user_id')
    role = identity.get('role')
    if role == 'admin':
        bookings = Booking.query.order_by(Booking.start_datetime.desc()).all()
    else:
        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.start_datetime.desc()).all()
    return jsonify({'bookings': [b.to_dict() for b in bookings]}), 200


@bookings_bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    identity = get_jwt_identity()
    user_id = identity.get('user_id')
    role = identity.get('role')
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != user_id and role != 'admin':
        return jsonify({'msg': 'Forbidden', 'code': 403}), 403
    return jsonify({'booking': booking.to_dict()}), 200


@bookings_bp.route('/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    identity = get_jwt_identity()
    user_id = identity.get('user_id')
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != user_id:
        return jsonify({'msg': 'Forbidden', 'code': 403}), 403
    if booking.status != 'pending':
        return jsonify({'msg': 'Only pending bookings can be updated', 'code': 400}), 400

    data = request.get_json() or {}
    address = data.get('address')
    notes = data.get('notes')
    start_iso = data.get('start_datetime')

    if start_iso:
        try:
            start_dt = parse_iso_to_utc(start_iso)
        except ValueError:
            return jsonify({'msg': 'Invalid start_datetime', 'code': 400}), 400
        now_utc = datetime.now(timezone.utc)
        if start_dt < now_utc + timedelta(minutes=10):
            return jsonify({'msg': 'start_datetime must be at least 10 minutes in the future', 'code': 400}), 400
        service = booking.service
        end_dt = start_dt + timedelta(minutes=service.duration_mins)
        if not business_hours_ok(start_dt, end_dt):
            return jsonify({'msg': 'Booking must be within business hours (08:00-19:00 UTC)', 'code': 400}), 400
        booking.start_datetime = start_dt
        booking.end_datetime = end_dt

    if address is not None:
        booking.address = address
    if notes is not None:
        booking.notes = notes

    db.session.commit()
    return jsonify({'msg': 'Booking updated', 'booking': booking.to_dict()}), 200


@bookings_bp.route('/<int:booking_id>', methods=['DELETE'])
@jwt_required()
def delete_booking(booking_id):
    identity = get_jwt_identity()
    user_id = identity.get('user_id')
    role = identity.get('role')
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != user_id and role != 'admin':
        return jsonify({'msg': 'Forbidden', 'code': 403}), 403
    if role != 'admin' and booking.status not in ('pending', 'confirmed'):
        return jsonify({'msg': 'Cannot cancel booking in its current status', 'code': 400}), 400

    booking.status = 'cancelled'
    db.session.commit()
    return jsonify({'msg': 'Booking cancelled'}), 200
