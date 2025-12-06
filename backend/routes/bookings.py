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


# Business hours configuration: 08:00-19:00 UTC
BUSINESS_HOURS_START = 8
BUSINESS_HOURS_END = 19
MIN_LEAD_TIME_HOURS = 3  # Minimum hours before booking start time
CANCELLATION_WINDOW_HOURS = 2  # Cannot cancel within 2 hours of start

def business_hours_ok(start_utc, end_utc):
    """
    Validate that booking times fall within business hours (08:00-19:00 UTC).
    Returns True if valid, False otherwise.
    """
    if start_utc.hour < BUSINESS_HOURS_START or end_utc.hour > BUSINESS_HOURS_END or (end_utc.hour == BUSINESS_HOURS_END and end_utc.minute > 0):
        return False
    return True

def calculate_price_total(service_price, areas_list):
    """
    Calculate total price: base price + area extras.
    Simple pricing: each area beyond the first adds $10.
    """
    base_price = service_price
    area_count = len(areas_list) if areas_list else 0
    area_extra = max(0, (area_count - 1) * 10)  # First area included, extras are $10 each
    # Add tax (8% example)
    subtotal = base_price + area_extra
    tax = subtotal * 0.08
    return round(subtotal + tax, 2)


@bookings_bp.route('', methods=['POST'])
@jwt_required()
def create_booking():
    """
    Create a booking for logged-in user.
    Validates: minimum lead time, business hours, and calculates price with area extras.
    """
    identity = get_jwt_identity()
    user_id = identity.get('user_id')
    data = request.get_json() or {}
    service_id = data.get('service_id')
    start_iso = data.get('start_datetime')
    address = data.get('address')
    notes = data.get('notes', '')
    areas = data.get('areas', [])  # List of selected areas
    payment_method = data.get('payment_method', 'cash')  # Default to cash

    # Validate required fields
    if not service_id or not start_iso:
        return jsonify({'success': False, 'msg': 'service_id and start_datetime required', 'code': 400}), 400

    if payment_method not in ['cash', 'cod', 'online']:
        return jsonify({'success': False, 'msg': 'payment_method must be cash, cod, or online', 'code': 400}), 400

    # Fetch and validate service
    service = ServiceType.query.get(service_id)
    if not service or not service.active:
        return jsonify({'success': False, 'msg': 'Service not found or inactive', 'code': 404}), 404

    # Parse and validate datetime
    try:
        start_dt = parse_iso_to_utc(start_iso)
    except ValueError:
        return jsonify({'success': False, 'msg': 'Invalid start_datetime format', 'code': 400}), 400

    now_utc = datetime.now(timezone.utc)
    min_start_time = now_utc + timedelta(hours=MIN_LEAD_TIME_HOURS)
    
    if start_dt < min_start_time:
        return jsonify({
            'success': False, 
            'msg': f'Booking must be at least {MIN_LEAD_TIME_HOURS} hours in the future', 
            'code': 400
        }), 400

    # Calculate end time and validate business hours
    end_dt = start_dt + timedelta(minutes=service.duration_mins)
    if not business_hours_ok(start_dt, end_dt):
        return jsonify({
            'success': False, 
            'msg': f'Booking must be within business hours ({BUSINESS_HOURS_START}:00-{BUSINESS_HOURS_END}:00 UTC)', 
            'code': 400
        }), 400

    # Calculate total price
    price_total = calculate_price_total(service.price, areas)

    # Create booking
    booking = Booking(
        user_id=user_id,
        service_id=service.id,
        start_datetime=start_dt,
        end_datetime=end_dt,
        address=address,
        notes=notes,
        payment_method=payment_method,
        price_total=price_total,
        status='pending'
    )
    booking.set_areas(areas)
    
    db.session.add(booking)
    db.session.commit()

    return jsonify({'success': True, 'data': booking.to_dict(), 'msg': 'Booking created'}), 201


@bookings_bp.route('', methods=['GET'])
@jwt_required()
def list_bookings():
    """
    List bookings for current user (or all bookings if admin).
    Supports filtering by status query parameter.
    """
    identity = get_jwt_identity()
    user_id = identity.get('user_id')
    role = identity.get('role')
    
    status_filter = request.args.get('status')
    
    if role == 'admin':
        query = Booking.query
        if status_filter:
            query = query.filter_by(status=status_filter)
        bookings = query.order_by(Booking.start_datetime.desc()).all()
    else:
        query = Booking.query.filter_by(user_id=user_id)
        if status_filter:
            query = query.filter_by(status=status_filter)
        bookings = query.order_by(Booking.start_datetime.desc()).all()
    
    return jsonify({'success': True, 'data': [b.to_dict() for b in bookings]}), 200


@bookings_bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    """Get booking details. Only owner or admin can view."""
    identity = get_jwt_identity()
    user_id = identity.get('user_id')
    role = identity.get('role')
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != user_id and role != 'admin':
        return jsonify({'success': False, 'msg': 'Forbidden', 'code': 403}), 403
    
    return jsonify({'success': True, 'data': booking.to_dict()}), 200


@bookings_bp.route('/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    """
    Update booking. Only owner can update, and only if status is 'pending'.
    Re-validates lead time and business hours if datetime is changed.
    """
    identity = get_jwt_identity()
    user_id = identity.get('user_id')
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != user_id:
        return jsonify({'success': False, 'msg': 'Forbidden', 'code': 403}), 403
    
    if booking.status != 'pending':
        return jsonify({'success': False, 'msg': 'Only pending bookings can be updated', 'code': 400}), 400

    data = request.get_json() or {}
    address = data.get('address')
    notes = data.get('notes')
    start_iso = data.get('start_datetime')
    areas = data.get('areas')

    # Update datetime if provided
    if start_iso:
        try:
            start_dt = parse_iso_to_utc(start_iso)
        except ValueError:
            return jsonify({'success': False, 'msg': 'Invalid start_datetime', 'code': 400}), 400
        
        now_utc = datetime.now(timezone.utc)
        min_start_time = now_utc + timedelta(hours=MIN_LEAD_TIME_HOURS)
        if start_dt < min_start_time:
            return jsonify({
                'success': False,
                'msg': f'Booking must be at least {MIN_LEAD_TIME_HOURS} hours in the future',
                'code': 400
            }), 400
        
        service = booking.service
        end_dt = start_dt + timedelta(minutes=service.duration_mins)
        if not business_hours_ok(start_dt, end_dt):
            return jsonify({
                'success': False,
                'msg': f'Booking must be within business hours ({BUSINESS_HOURS_START}:00-{BUSINESS_HOURS_END}:00 UTC)',
                'code': 400
            }), 400
        
        booking.start_datetime = start_dt
        booking.end_datetime = end_dt

    # Update other fields
    if address is not None:
        booking.address = address
    if notes is not None:
        booking.notes = notes
    if areas is not None:
        booking.set_areas(areas)
        # Recalculate price if areas changed
        booking.price_total = calculate_price_total(booking.service.price, areas)

    db.session.commit()
    return jsonify({'success': True, 'data': booking.to_dict(), 'msg': 'Booking updated'}), 200


@bookings_bp.route('/<int:booking_id>', methods=['DELETE'])
@jwt_required()
def delete_booking(booking_id):
    """
    Cancel a booking. Users can cancel if pending/confirmed and outside cancellation window.
    Admins can cancel anytime.
    """
    identity = get_jwt_identity()
    user_id = identity.get('user_id')
    role = identity.get('role')
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != user_id and role != 'admin':
        return jsonify({'success': False, 'msg': 'Forbidden', 'code': 403}), 403
    
    # Non-admin cancellation rules
    if role != 'admin':
        if booking.status not in ('pending', 'confirmed'):
            return jsonify({
                'success': False,
                'msg': 'Cannot cancel booking in its current status',
                'code': 400
            }), 400
        
        # Check cancellation window: cannot cancel within 2 hours of start
        now_utc = datetime.now(timezone.utc)
        cancellation_deadline = booking.start_datetime - timedelta(hours=CANCELLATION_WINDOW_HOURS)
        if now_utc > cancellation_deadline:
            return jsonify({
                'success': False,
                'msg': f'Cannot cancel within {CANCELLATION_WINDOW_HOURS} hours of booking start',
                'code': 400
            }), 400

    booking.status = 'cancelled'
    db.session.commit()
    return jsonify({'success': True, 'msg': 'Booking cancelled', 'data': booking.to_dict()}), 200
