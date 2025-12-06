from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Booking, Cleaner
from datetime import datetime, timedelta, timezone

admin_bp = Blueprint('admin', __name__)


def admin_only(identity):
    if identity.get('role') != 'admin':
        return False
    return True


@admin_bp.route('/bookings', methods=['GET'])
@jwt_required()
def list_all_bookings():
    identity = get_jwt_identity()
    if not admin_only(identity):
        return jsonify({'msg': 'Admin only', 'code': 403}), 403

    # optional filters
    date = request.args.get('date')
    status = request.args.get('status')
    query = Booking.query
    if date:
        # filter by date (YYYY-MM-DD)
        try:
            d = datetime.fromisoformat(date).date()
            query = query.filter(db.func.date(Booking.start_datetime) == d)
        except Exception:
            pass
    if status:
        query = query.filter_by(status=status)
    bookings = query.order_by(Booking.start_datetime.desc()).all()
    return jsonify({'bookings': [b.to_dict() for b in bookings]}), 200


@admin_bp.route('/bookings/<int:booking_id>/assign', methods=['PUT'])
@jwt_required()
def assign_cleaner(booking_id):
    identity = get_jwt_identity()
    if not admin_only(identity):
        return jsonify({'msg': 'Admin only', 'code': 403}), 403
    data = request.get_json() or {}
    cleaner_id = data.get('cleaner_id')
    if not cleaner_id:
        return jsonify({'msg': 'cleaner_id required', 'code': 400}), 400
    booking = Booking.query.get_or_404(booking_id)
    cleaner = Cleaner.query.get(cleaner_id)
    if not cleaner:
        return jsonify({'msg': 'Cleaner not found', 'code': 404}), 404

    # check conflicts for cleaner
    overlapping = Booking.query.filter(
        Booking.cleaner_id == cleaner.id,
        Booking.id != booking.id,
        Booking.status != 'cancelled',
        db.or_(
            db.and_(Booking.start_datetime <= booking.start_datetime, Booking.end_datetime > booking.start_datetime),
            db.and_(Booking.start_datetime < booking.end_datetime, Booking.end_datetime >= booking.end_datetime),
            db.and_(Booking.start_datetime >= booking.start_datetime, Booking.end_datetime <= booking.end_datetime),
        )
    ).first()
    if overlapping:
        return jsonify({'msg': 'Cleaner has conflicting booking', 'code': 400}), 400

    booking.cleaner_id = cleaner.id
    booking.status = 'confirmed'
    db.session.commit()
    return jsonify({'msg': 'Cleaner assigned', 'booking': booking.to_dict()}), 200


@admin_bp.route('/bookings/<int:booking_id>/status', methods=['PUT'])
@jwt_required()
def update_status(booking_id):
    identity = get_jwt_identity()
    if not admin_only(identity):
        return jsonify({'msg': 'Admin only', 'code': 403}), 403
    data = request.get_json() or {}
    status = data.get('status')
    if status not in ('in_progress', 'completed', 'cancelled', 'confirmed'):
        return jsonify({'msg': 'Invalid status', 'code': 400}), 400
    booking = Booking.query.get_or_404(booking_id)
    booking.status = status
    db.session.commit()
    return jsonify({'msg': 'Status updated', 'booking': booking.to_dict()}), 200


@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def stats():
    identity = get_jwt_identity()
    if not admin_only(identity):
        return jsonify({'msg': 'Admin only', 'code': 403}), 403

    counts = {
        'pending': Booking.query.filter_by(status='pending').count(),
        'confirmed': Booking.query.filter_by(status='confirmed').count(),
        'in_progress': Booking.query.filter_by(status='in_progress').count(),
        'completed': Booking.query.filter_by(status='completed').count(),
        'cancelled': Booking.query.filter_by(status='cancelled').count(),
    }

    # daily counts for past 7 days
    daily = []
    today = datetime.now(timezone.utc).date()
    for i in range(7):
        d = today - timedelta(days=i)
        c = Booking.query.filter(db.func.date(Booking.created_at) == d).count()
        daily.append({'date': d.isoformat(), 'count': c})

    return jsonify({'counts': counts, 'daily': daily}), 200
