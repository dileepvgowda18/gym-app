from datetime import date

from flask import Blueprint, jsonify
from app.models import User, Payment, Membership, Booking, GymClass, Plan, Trainer
from app.decorators import roles_required
from app.extensions import db
from sqlalchemy import func

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/members")
@roles_required("admin")
def list_members():
    members = User.query.filter_by(role="member").order_by(User.created_at.desc()).all()
    result = []
    for member in members:
        payload = member.to_dict()
        latest_membership = max(
            member.memberships,
            key=lambda membership: membership.start_date or date.min,
            default=None,
        )
        payload["membership_status"] = latest_membership.status if latest_membership else "none"
        result.append(payload)
    return jsonify(result)


@admin_bp.get("/plans")
@roles_required("admin")
def list_plans():
    plans = Plan.query.order_by(Plan.price.asc()).all()
    return jsonify([plan.to_dict() for plan in plans])


@admin_bp.get("/trainers")
@roles_required("admin")
def list_trainers():
    trainers = Trainer.query.order_by(Trainer.id.asc()).all()
    return jsonify([trainer.to_dict() for trainer in trainers])


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
