import math

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Plan
from app.decorators import roles_required

plans_bp = Blueprint("plans", __name__, url_prefix="/api/plans")


def _plan_payload(data, partial=False):
    if not isinstance(data, dict):
        return None, "request body must be a JSON object"

    payload = {}
    if not partial or "name" in data:
        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            return None, "name is required"
        if len(name.strip()) > 80:
            return None, "name must be 80 characters or fewer"
        payload["name"] = name.strip()

    if not partial or "price" in data:
        try:
            price = float(data.get("price"))
        except (TypeError, ValueError):
            return None, "price must be a non-negative number"
        if not math.isfinite(price) or price < 0:
            return None, "price must be a non-negative number"
        payload["price"] = price

    if not partial or "duration_days" in data:
        try:
            raw_duration = data.get("duration_days")
            numeric_duration = float(raw_duration)
        except (TypeError, ValueError):
            return None, "duration_days must be a positive whole number"
        if (
            isinstance(raw_duration, bool)
            or not math.isfinite(numeric_duration)
            or not numeric_duration.is_integer()
            or numeric_duration < 1
        ):
            return None, "duration_days must be a positive whole number"
        payload["duration_days"] = int(numeric_duration)

    if not partial or "features" in data:
        features = data.get("features", [])
        if not isinstance(features, list) or not all(isinstance(item, str) for item in features):
            return None, "features must be an array of strings"
        payload["features"] = [feature.strip() for feature in features if feature.strip()]

    if partial and "is_active" in data:
        if not isinstance(data["is_active"], bool):
            return None, "is_active must be a boolean"
        payload["is_active"] = data["is_active"]

    return payload, None


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
    payload, error = _plan_payload(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400
    plan = Plan(**payload)
    db.session.add(plan)
    db.session.commit()
    return jsonify(plan.to_dict()), 201


@plans_bp.put("/<int:plan_id>")
@roles_required("admin")
def update_plan(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    payload, error = _plan_payload(request.get_json(silent=True), partial=True)
    if error:
        return jsonify({"error": error}), 400
    for field, value in payload.items():
        setattr(plan, field, value)
    db.session.commit()
    return jsonify(plan.to_dict())


@plans_bp.delete("/<int:plan_id>")
@roles_required("admin")
def delete_plan(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    plan.is_active = False
    db.session.commit()
    return jsonify({"message": "plan deactivated"})
