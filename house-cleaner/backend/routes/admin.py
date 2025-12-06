from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Booking, Cleaner, User, ServiceType, Review
from datetime import datetime, timedelta, timezone
import csv
import io

admin_bp = Blueprint('admin', __name__)


def admin_only(identity):
    """Helper function to check if user is admin"""
    return identity and identity.get('role') == 'admin'


@admin_bp.route('/bookings', methods=['GET'])
@jwt_required()
def list_all_bookings():
    """
    List all bookings with optional filters.
    Query params: date (YYYY-MM-DD), status, service_id, cleaner_id
    """
    identity = get_jwt_identity()
    if not admin_only(identity):
        return jsonify({'success': False, 'msg': 'Admin only', 'code': 403}), 403

    # Optional filters
    date = request.args.get('date')
    status = request.args.get('status')
    service_id = request.args.get('service_id', type=int)
    cleaner_id = request.args.get('cleaner_id', type=int)
    
    query = Booking.query
    
    if date:
        # Filter by date (YYYY-MM-DD)
        try:
            d = datetime.fromisoformat(date).date()
            query = query.filter(db.func.date(Booking.start_datetime) == d)
        except Exception:
            pass
    if status:
        query = query.filter_by(status=status)
    if service_id:
        query = query.filter_by(service_id=service_id)
    if cleaner_id:
        query = query.filter_by(cleaner_id=cleaner_id)
    
    bookings = query.order_by(Booking.start_datetime.desc()).all()
    return jsonify({'success': True, 'data': [b.to_dict() for b in bookings]}), 200


@admin_bp.route('/bookings/<int:booking_id>/assign', methods=['PUT'])
@jwt_required()
def assign_cleaner(booking_id):
    """
    Assign a cleaner to a booking and set status to confirmed.
    Validates that cleaner is active and has no time conflicts.
    """
    identity = get_jwt_identity()
    if not admin_only(identity):
        return jsonify({'success': False, 'msg': 'Admin only', 'code': 403}), 403
    
    data = request.get_json() or {}
    cleaner_id = data.get('cleaner_id')
    
    if not cleaner_id:
        return jsonify({'success': False, 'msg': 'cleaner_id required', 'code': 400}), 400
    
    booking = Booking.query.get_or_404(booking_id)
    cleaner = Cleaner.query.get(cleaner_id)
    
    if not cleaner:
        return jsonify({'success': False, 'msg': 'Cleaner not found', 'code': 404}), 404
    
    if not cleaner.active:
        return jsonify({'success': False, 'msg': 'Cleaner is not active', 'code': 400}), 400

    # Check for time conflicts: cleaner cannot have overlapping bookings
    overlapping = Booking.query.filter(
        Booking.cleaner_id == cleaner.id,
        Booking.id != booking.id,
        Booking.status != 'cancelled',
        db.or_(
            db.and_(
                Booking.start_datetime <= booking.start_datetime,
                Booking.end_datetime > booking.start_datetime
            ),
            db.and_(
                Booking.start_datetime < booking.end_datetime,
                Booking.end_datetime >= booking.end_datetime
            ),
            db.and_(
                Booking.start_datetime >= booking.start_datetime,
                Booking.end_datetime <= booking.end_datetime
            ),
        )
    ).first()
    
    if overlapping:
        return jsonify({
            'success': False,
            'msg': 'Cleaner has conflicting booking at that time',
            'code': 400
        }), 400

    booking.cleaner_id = cleaner.id
    booking.status = 'confirmed'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': booking.to_dict(),
        'msg': 'Cleaner assigned'
    }), 200


@admin_bp.route('/bookings/<int:booking_id>/status', methods=['PUT'])
@jwt_required()
def update_status(booking_id):
    """
    Update booking status. Valid statuses: pending, confirmed, in_progress, completed, cancelled.
    When setting to 'completed', users can then post reviews.
    """
    identity = get_jwt_identity()
    if not admin_only(identity):
        return jsonify({'success': False, 'msg': 'Admin only', 'code': 403}), 403
    
    data = request.get_json() or {}
    status = data.get('status')
    
    valid_statuses = ('pending', 'confirmed', 'in_progress', 'completed', 'cancelled')
    if status not in valid_statuses:
        return jsonify({
            'success': False,
            'msg': f'Invalid status. Must be one of: {", ".join(valid_statuses)}',
            'code': 400
        }), 400
    
    booking = Booking.query.get_or_404(booking_id)
    booking.status = status
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': booking.to_dict(),
        'msg': 'Status updated'
    }), 200


@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def stats():
    """
    Get admin statistics: booking counts by status, daily counts for past 7 days,
    revenue estimate, and top services.
    """
    identity = get_jwt_identity()
    if not admin_only(identity):
        return jsonify({'success': False, 'msg': 'Admin only', 'code': 403}), 403

    # Count bookings by status
    counts = {
        'pending': Booking.query.filter_by(status='pending').count(),
        'confirmed': Booking.query.filter_by(status='confirmed').count(),
        'in_progress': Booking.query.filter_by(status='in_progress').count(),
        'completed': Booking.query.filter_by(status='completed').count(),
        'cancelled': Booking.query.filter_by(status='cancelled').count(),
    }

    # Daily counts for past 7 days
    daily = []
    today = datetime.now(timezone.utc).date()
    revenue_past_7_days = 0.0
    
    for i in range(7):
        d = today - timedelta(days=i)
        day_bookings = Booking.query.filter(
            db.func.date(Booking.created_at) == d
        ).all()
        c = len(day_bookings)
        # Calculate revenue for completed bookings
        day_revenue = sum(b.price_total for b in day_bookings if b.status == 'completed')
        revenue_past_7_days += day_revenue
        daily.append({
            'date': d.isoformat(),
            'count': c,
            'revenue': round(day_revenue, 2)
        })

    # Top services (count of bookings per service)
    service_stats = db.session.query(
        ServiceType.id,
        ServiceType.name,
        db.func.count(Booking.id).label('booking_count')
    ).join(Booking).group_by(ServiceType.id, ServiceType.name).order_by(
        db.func.count(Booking.id).desc()
    ).limit(5).all()
    
    top_services = [
        {'service_id': s[0], 'name': s[1], 'booking_count': s[2]}
        for s in service_stats
    ]

    return jsonify({
        'success': True,
        'data': {
            'counts': counts,
            'daily': daily,
            'revenue_past_7_days': round(revenue_past_7_days, 2),
            'top_services': top_services
        }
    }), 200

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    """List all users with their booking counts. Admin only."""
    identity = get_jwt_identity()
    if not admin_only(identity):
        return jsonify({'success': False, 'msg': 'Admin only', 'code': 403}), 403

    users = User.query.all()
    users_data = []
    for user in users:
        user_dict = user.to_dict()
        booking_count = Booking.query.filter_by(user_id=user.id).count()
        user_dict['booking_count'] = booking_count
        users_data.append(user_dict)

    return jsonify({'success': True, 'data': users_data}), 200

@admin_bp.route('/cleaners', methods=['GET'])
@jwt_required()
def list_cleaners():
    """List all cleaners. Admin only."""
    identity = get_jwt_identity()
    if not admin_only(identity):
        return jsonify({'success': False, 'msg': 'Admin only', 'code': 403}), 403

    cleaners = Cleaner.query.order_by(Cleaner.name).all()
    return jsonify({'success': True, 'data': [c.to_dict() for c in cleaners]}), 200

@admin_bp.route('/cleaners', methods=['POST'])
@jwt_required()
def create_cleaner():
    """Create a new cleaner. Admin only."""
    identity = get_jwt_identity()
    if not admin_only(identity):
        return jsonify({'success': False, 'msg': 'Admin only', 'code': 403}), 403

    data = request.get_json() or {}
    name = data.get('name')
    phone = data.get('phone', '')
    
    if not name:
        return jsonify({'success': False, 'msg': 'name required', 'code': 400}), 400

    cleaner = Cleaner(name=name, phone=phone, active=data.get('active', True))
    db.session.add(cleaner)
    db.session.commit()

    return jsonify({'success': True, 'data': cleaner.to_dict(), 'msg': 'Cleaner created'}), 201

@admin_bp.route('/cleaners/<int:cleaner_id>', methods=['PUT'])
@jwt_required()
def update_cleaner(cleaner_id):
    """Update cleaner information. Admin only."""
    identity = get_jwt_identity()
    if not admin_only(identity):
        return jsonify({'success': False, 'msg': 'Admin only', 'code': 403}), 403

    cleaner = Cleaner.query.get_or_404(cleaner_id)
    data = request.get_json() or {}

    if 'name' in data:
        cleaner.name = data['name']
    if 'phone' in data:
        cleaner.phone = data['phone']
    if 'active' in data:
        cleaner.active = data['active']

    db.session.commit()
    return jsonify({'success': True, 'data': cleaner.to_dict(), 'msg': 'Cleaner updated'}), 200

@admin_bp.route('/bookings/export', methods=['GET'])
@jwt_required()
def export_bookings_csv():
    """Export bookings to CSV. Admin only."""
    identity = get_jwt_identity()
    if not admin_only(identity):
        return jsonify({'success': False, 'msg': 'Admin only', 'code': 403}), 403

    # Get all bookings
    bookings = Booking.query.order_by(Booking.start_datetime.desc()).all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'User Email', 'Service', 'Cleaner', 'Start Time', 'End Time',
        'Status', 'Areas', 'Payment Method', 'Total Price', 'Address', 'Created At'
    ])
    
    # Write data rows
    for booking in bookings:
        writer.writerow([
            booking.id,
            booking.user.email if booking.user else '',
            booking.service.name if booking.service else '',
            booking.cleaner.name if booking.cleaner else 'Unassigned',
            booking.start_datetime.isoformat() if booking.start_datetime else '',
            booking.end_datetime.isoformat() if booking.end_datetime else '',
            booking.status,
            ', '.join(booking.get_areas()) if booking.get_areas() else '',
            booking.payment_method,
            booking.price_total,
            booking.address or '',
            booking.created_at.isoformat() if booking.created_at else ''
        ])

    # Create response with CSV
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=bookings_export.csv'
    return response
