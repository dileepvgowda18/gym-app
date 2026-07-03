from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Plan
from app.decorators import roles_required

plans_bp = Blueprint("plans", __name__, url_prefix="/api/plans")


@plans_bp.get("")
def list_plans():
    plans = Plan.query.filter_by(is_active=True).order_by(Plan.price.asc()).all()
    return jsonify([p.to_dict() for p in plans])


@plans_bp.get("/<int:plan_id>")
def get_plan(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    return jsonify(plan.to_dict())


@plans_bp.post("")
@roles_required("admin")
def create_plan():
    data = request.get_json() or {}
    plan = Plan(
        name=data.get("name"),
        price=data.get("price"),
        duration_days=data.get("duration_days"),
        features=data.get("features", []),
    )
    db.session.add(plan)
    db.session.commit()
    return jsonify(plan.to_dict()), 201


@plans_bp.put("/<int:plan_id>")
@roles_required("admin")
def update_plan(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    data = request.get_json() or {}
    for field in ("name", "price", "duration_days", "features", "is_active"):
        if field in data:
            setattr(plan, field, data[field])
    db.session.commit()
    return jsonify(plan.to_dict())


@plans_bp.delete("/<int:plan_id>")
@roles_required("admin")
def delete_plan(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    db.session.delete(plan)
    db.session.commit()
    return jsonify({"message": "plan deleted"})
