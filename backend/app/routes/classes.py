from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import GymClass, Trainer
from app.decorators import roles_required

classes_bp = Blueprint("classes", __name__, url_prefix="/api/classes")


@classes_bp.get("")
def list_classes():
    classes = GymClass.query.all()
    return jsonify([c.to_dict() for c in classes])


@classes_bp.get("/<int:class_id>")
def get_class(class_id):
    gym_class = GymClass.query.get_or_404(class_id)
    return jsonify(gym_class.to_dict())


@classes_bp.post("")
@roles_required("admin", "trainer")
def create_class():
    data = request.get_json() or {}
    gym_class = GymClass(
        name=data.get("name"),
        trainer_id=data.get("trainer_id"),
        schedule_day=data.get("schedule_day"),
        schedule_time=data.get("schedule_time"),
        duration_minutes=data.get("duration_minutes", 60),
        capacity=data.get("capacity", 20),
        description=data.get("description"),
    )
    db.session.add(gym_class)
    db.session.commit()
    return jsonify(gym_class.to_dict()), 201


@classes_bp.put("/<int:class_id>")
@roles_required("admin", "trainer")
def update_class(class_id):
    gym_class = GymClass.query.get_or_404(class_id)
    data = request.get_json() or {}
    for field in ("name", "trainer_id", "schedule_day", "schedule_time", "duration_minutes", "capacity", "description"):
        if field in data:
            setattr(gym_class, field, data[field])
    db.session.commit()
    return jsonify(gym_class.to_dict())


@classes_bp.delete("/<int:class_id>")
@roles_required("admin")
def delete_class(class_id):
    gym_class = GymClass.query.get_or_404(class_id)
    db.session.delete(gym_class)
    db.session.commit()
    return jsonify({"message": "class deleted"})
