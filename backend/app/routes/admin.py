from flask import Blueprint, jsonify
from app.models import User, Payment, Membership, Booking, GymClass
from app.decorators import roles_required
from app.extensions import db
from sqlalchemy import func

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/members")
@roles_required("admin")
def list_members():
    members = User.query.filter_by(role="member").all()
    return jsonify([m.to_dict() for m in members])


@admin_bp.get("/stats")
@roles_required("admin")
def stats():
    total_members = User.query.filter_by(role="member").count()
    active_memberships = Membership.query.filter_by(status="active").count()
    total_revenue = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.status == "completed"
    ).scalar()
    total_bookings = Booking.query.filter_by(status="confirmed").count()
    total_classes = GymClass.query.count()

    return jsonify({
        "total_members": total_members,
        "active_memberships": active_memberships,
        "total_revenue": float(total_revenue),
        "total_bookings": total_bookings,
        "total_classes": total_classes,
    })
