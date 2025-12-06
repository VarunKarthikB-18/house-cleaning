from flask import Blueprint, request, jsonify
from extensions import db
from models import Review, Booking, User
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/reviews', methods=['POST'])
@jwt_required()
def create_review():
    """
    Create a review for a completed booking.
    Only the booking owner can create a review, and only if booking status is 'completed'.
    """
    data = request.get_json() or {}
    booking_id = data.get('booking_id')
    rating = data.get('rating')
    comment = data.get('comment', '')

    # Validate required fields
    if not booking_id or not rating:
        return jsonify({'success': False, 'msg': 'booking_id and rating required', 'code': 400}), 400

    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'success': False, 'msg': 'Rating must be between 1 and 5', 'code': 400}), 400

    # Get current user identity
    identity = get_jwt_identity() or {}
    user_id = identity.get('user_id')

    # Fetch booking and verify ownership and status
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'success': False, 'msg': 'Booking not found', 'code': 404}), 404

    if booking.user_id != user_id:
        return jsonify({'success': False, 'msg': 'Unauthorized', 'code': 403}), 403

    if booking.status != 'completed':
        return jsonify({'success': False, 'msg': 'Can only review completed bookings', 'code': 400}), 400

    # Check if review already exists for this booking
    existing_review = Review.query.filter_by(booking_id=booking_id).first()
    if existing_review:
        return jsonify({'success': False, 'msg': 'Review already exists for this booking', 'code': 400}), 400

    # Create new review
    review = Review(
        user_id=user_id,
        booking_id=booking_id,
        rating=rating,
        comment=comment,
        moderated=False
    )
    db.session.add(review)
    db.session.commit()

    return jsonify({'success': True, 'data': review.to_dict(), 'msg': 'Review created'}), 201

@reviews_bp.route('/reviews', methods=['GET'])
def get_reviews():
    """
    Get reviews. Supports query parameters:
    - booking_id: filter by booking
    - user_id: filter by user (admin only, or own user_id)
    Note: This endpoint is public for viewing reviews, but filtering by user_id requires auth.
    """
    # Try to get identity if token is present (optional auth)
    current_user_role = 'user'
    current_user_id = None
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            current_user_role = identity.get('role', 'user')
            current_user_id = identity.get('user_id')
    except:
        # No token provided or invalid - that's okay for public viewing
        pass

    booking_id = request.args.get('booking_id', type=int)
    user_id = request.args.get('user_id', type=int)

    # Build query
    query = Review.query

    if booking_id:
        query = query.filter_by(booking_id=booking_id)

    if user_id:
        # Only admins can filter by other users, or users can see their own
        if current_user_role == 'admin':
            query = query.filter_by(user_id=user_id)
        elif current_user_id and current_user_id == user_id:
            # Users can see their own reviews
            query = query.filter_by(user_id=user_id)
        else:
            return jsonify({'success': False, 'msg': 'Unauthorized', 'code': 403}), 403

    reviews = query.order_by(Review.created_at.desc()).all()
    return jsonify({'success': True, 'data': [r.to_dict() for r in reviews]}), 200

@reviews_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """Delete a review. Only admins can delete reviews."""
    identity = get_jwt_identity() or {}
    role = identity.get('role')

    if role != 'admin':
        return jsonify({'success': False, 'msg': 'Admin access required', 'code': 403}), 403

    review = Review.query.get(review_id)
    if not review:
        return jsonify({'success': False, 'msg': 'Review not found', 'code': 404}), 404

    db.session.delete(review)
    db.session.commit()

    return jsonify({'success': True, 'msg': 'Review deleted'}), 200

