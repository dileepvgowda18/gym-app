import uuid
from datetime import date, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.extensions import db
from app.models import Membership, Payment, Plan

payments_bp = Blueprint("payments", __name__, url_prefix="/api")


@payments_bp.post("/memberships/subscribe")
@jwt_required()
def subscribe():
    """Create a membership + a (simulated) payment in one step."""
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    plan_id = data.get("plan_id")

    plan = Plan.query.get_or_404(plan_id)
    start = date.today()
    end = start + timedelta(days=plan.duration_days)

    membership = Membership(user_id=user_id, plan_id=plan.id, start_date=start, end_date=end, status="active")
    db.session.add(membership)
    db.session.flush()

    payment = Payment(
        user_id=user_id,
        membership_id=membership.id,
        amount=plan.price,
        status="completed",
        transaction_id=str(uuid.uuid4()),
        method=data.get("method", "card"),
    )
    db.session.add(payment)
    db.session.commit()

    return jsonify({"membership": membership.to_dict(), "payment": payment.to_dict()}), 201


@payments_bp.get("/memberships")
@jwt_required()
def list_memberships():
    user_id = get_jwt_identity()
    claims = get_jwt()
    if claims.get("role") == "admin":
        memberships = Membership.query.all()
    else:
        memberships = Membership.query.filter_by(user_id=user_id).all()
    return jsonify([m.to_dict() for m in memberships])


@payments_bp.get("/payments")
@jwt_required()
def list_payments():
    user_id = get_jwt_identity()
    claims = get_jwt()
    if claims.get("role") == "admin":
        payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    else:
        payments = Payment.query.filter_by(user_id=user_id).order_by(Payment.payment_date.desc()).all()
    return jsonify([p.to_dict() for p in payments])
