from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.extensions import db
from app.models import Booking, GymClass

bookings_bp = Blueprint("bookings", __name__, url_prefix="/api/bookings")


@bookings_bp.get("")
@jwt_required()
def list_bookings():
    user_id = get_jwt_identity()
    claims = get_jwt()
    if claims.get("role") == "admin":
        bookings = Booking.query.all()
    else:
        bookings = Booking.query.filter_by(user_id=user_id).all()
    return jsonify([b.to_dict() for b in bookings])


@bookings_bp.post("")
@jwt_required()
def create_booking():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    class_id = data.get("class_id")

    gym_class = GymClass.query.get_or_404(class_id)
    active_bookings = Booking.query.filter_by(class_id=class_id, status="confirmed").count()
    if active_bookings >= gym_class.capacity:
        return jsonify({"error": "this class is full"}), 400

    existing = Booking.query.filter_by(user_id=user_id, class_id=class_id, status="confirmed").first()
    if existing:
        return jsonify({"error": "you already booked this class"}), 409

    booking = Booking(user_id=user_id, class_id=class_id, status="confirmed")
    db.session.add(booking)
    db.session.commit()
    return jsonify(booking.to_dict()), 201


@bookings_bp.delete("/<int:booking_id>")
@jwt_required()
def cancel_booking(booking_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    booking = Booking.query.get_or_404(booking_id)

    if str(booking.user_id) != str(user_id) and claims.get("role") != "admin":
        return jsonify({"error": "you do not have permission to cancel this booking"}), 403

    booking.status = "cancelled"
    db.session.commit()
    return jsonify(booking.to_dict())
