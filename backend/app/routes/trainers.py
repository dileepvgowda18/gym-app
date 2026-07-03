from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Trainer, User
from app.decorators import roles_required

trainers_bp = Blueprint("trainers", __name__, url_prefix="/api/trainers")


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
    data = request.get_json() or {}
    # Creates a linked user with role=trainer, plus trainer profile
    user = User(
        name=data.get("name"),
        email=data.get("email", "").strip().lower(),
        phone=data.get("phone", ""),
        role="trainer",
    )
    user.set_password(data.get("password", "changeme123"))
    db.session.add(user)
    db.session.flush()

    trainer = Trainer(
        user_id=user.id,
        specialization=data.get("specialization"),
        bio=data.get("bio"),
        image_url=data.get("image_url"),
        years_experience=data.get("years_experience", 0),
    )
    db.session.add(trainer)
    db.session.commit()
    return jsonify(trainer.to_dict()), 201


@trainers_bp.put("/<int:trainer_id>")
@roles_required("admin")
def update_trainer(trainer_id):
    trainer = Trainer.query.get_or_404(trainer_id)
    data = request.get_json() or {}
    for field in ("specialization", "bio", "image_url", "years_experience"):
        if field in data:
            setattr(trainer, field, data[field])
    db.session.commit()
    return jsonify(trainer.to_dict())


@trainers_bp.delete("/<int:trainer_id>")
@roles_required("admin")
def delete_trainer(trainer_id):
    trainer = Trainer.query.get_or_404(trainer_id)
    db.session.delete(trainer)
    db.session.commit()
    return jsonify({"message": "trainer deleted"})
