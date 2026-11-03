import re

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Trainer, User
from app.decorators import roles_required

trainers_bp = Blueprint("trainers", __name__, url_prefix="/api/trainers")


def _trainer_data(data, partial=False):
    if not isinstance(data, dict):
        return None, "request body must be a JSON object"

    payload = {}
    if not partial or "name" in data:
        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            return None, "name is required"
        if len(name.strip()) > 120:
            return None, "name must be 120 characters or fewer"
        payload["name"] = name.strip()

    if not partial or "email" in data:
        email = data.get("email")
        if not isinstance(email, str) or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()):
            return None, "a valid email is required"
        payload["email"] = email.strip().lower()

    if not partial or "specialization" in data:
        specialization = data.get("specialization")
        if not isinstance(specialization, str) or not specialization.strip():
            return None, "specialization is required"
        if len(specialization.strip()) > 120:
            return None, "specialization must be 120 characters or fewer"
        payload["specialization"] = specialization.strip()

    if not partial or "years_experience" in data:
        try:
            raw_years = data.get("years_experience", 0)
            numeric_years = float(raw_years)
        except (TypeError, ValueError):
            return None, "years_experience must be a non-negative whole number"
        if (
            isinstance(raw_years, bool)
            or not numeric_years.is_integer()
            or numeric_years < 0
        ):
            return None, "years_experience must be a non-negative whole number"
        payload["years_experience"] = int(numeric_years)

    for field in ("bio", "image_url"):
        if field in data:
            if data[field] is not None and not isinstance(data[field], str):
                return None, f"{field} must be a string"
            payload[field] = data[field].strip() if data[field] else None

    if "password" in data:
        if not isinstance(data["password"], str) or len(data["password"]) < 8:
            return None, "password must be at least 8 characters"
        payload["password"] = data["password"]
    elif not partial:
        return None, "password is required"

    return payload, None


@trainers_bp.get("")
def list_trainers():
    trainers = Trainer.query.all()
    return jsonify([t.to_dict() for t in trainers])


@trainers_bp.get("/<int:trainer_id>")
def get_trainer(trainer_id):
    trainer = Trainer.query.get_or_404(trainer_id)
    return jsonify(trainer.to_dict())


@trainers_bp.post("")
@roles_required("admin")
def create_trainer():
    payload, error = _trainer_data(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400
    if User.query.filter_by(email=payload["email"]).first():
        return jsonify({"error": "an account with this email already exists"}), 409

    user = User(
        name=payload["name"],
        email=payload["email"],
        phone="",
        role="trainer",
    )
    user.set_password(payload["password"])
    db.session.add(user)
    db.session.flush()

    trainer = Trainer(
        user_id=user.id,
        specialization=payload["specialization"],
        bio=payload.get("bio"),
        image_url=payload.get("image_url"),
        years_experience=payload["years_experience"],
    )
    db.session.add(trainer)
    db.session.commit()
    return jsonify(trainer.to_dict()), 201


@trainers_bp.put("/<int:trainer_id>")
@roles_required("admin")
def update_trainer(trainer_id):
    trainer = Trainer.query.get_or_404(trainer_id)
    payload, error = _trainer_data(request.get_json(silent=True), partial=True)
    if error:
        return jsonify({"error": error}), 400
    if "email" in payload and User.query.filter(
        User.email == payload["email"], User.id != trainer.user_id
    ).first():
        return jsonify({"error": "an account with this email already exists"}), 409

    if "name" in payload:
        trainer.user.name = payload.pop("name")
    if "email" in payload:
        trainer.user.email = payload.pop("email")
    if "password" in payload:
        trainer.user.set_password(payload.pop("password"))
    for field, value in payload.items():
        setattr(trainer, field, value)
    db.session.commit()
    return jsonify(trainer.to_dict())


@trainers_bp.delete("/<int:trainer_id>")
@roles_required("admin")
def delete_trainer(trainer_id):
    trainer = Trainer.query.get_or_404(trainer_id)
    dependencies = []
    if trainer.classes:
        dependencies.append("scheduled classes")
    if trainer.appointments:
        dependencies.append("appointments")
    if trainer.workout_plans:
        dependencies.append("workout plans")
    if dependencies:
        return jsonify({
            "error": "trainer has existing " + ", ".join(dependencies) + " and cannot be removed"
        }), 409

    trainer.user.role = "member"
    db.session.delete(trainer)
    db.session.commit()
    return jsonify({"message": "trainer profile removed; login account retained as a member"})
