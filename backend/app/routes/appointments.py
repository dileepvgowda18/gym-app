from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models import Trainer, TrainerAppointment

appointments_bp = Blueprint("appointments", __name__, url_prefix="/api")


@appointments_bp.get("/trainers/<int:trainer_id>/availability")
def get_trainer_availability(trainer_id):
    Trainer.query.get_or_404(trainer_id)
    date_param = request.args.get("date")
    if not date_param:
        return jsonify({"slots": []})

    try:
        start_day = datetime.fromisoformat(date_param)
    except ValueError:
        return jsonify({"error": "invalid date format"}), 400

    slots = []
    for hour in [6, 7, 8, 9, 10, 11, 17, 18, 19]:
        slot_start = start_day.replace(hour=hour, minute=0, second=0, microsecond=0)
        slot_end = slot_start.replace(hour=hour + 1)
        conflict = TrainerAppointment.query.filter(
            TrainerAppointment.trainer_id == trainer_id,
            TrainerAppointment.status.in_(["pending", "confirmed", "completed"]),
            TrainerAppointment.start_at < slot_end,
            TrainerAppointment.end_at > slot_start,
        ).first()
        if not conflict:
            slots.append({"start": slot_start.isoformat(), "end": slot_end.isoformat()})
    return jsonify({"slots": slots})


@appointments_bp.post("/appointments")
@jwt_required()
def create_appointment():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get("role") != "member":
        return jsonify({"error": "member access required"}), 403

    data = request.get_json() or {}
    trainer_id = data.get("trainer_id")
    start_at = data.get("start_at")
    if not trainer_id or not start_at:
        return jsonify({"error": "trainer_id and start_at are required"}), 400

    try:
        start_dt = datetime.fromisoformat(start_at)
    except ValueError:
        return jsonify({"error": "invalid start_at format"}), 400

    end_dt = start_dt.replace(hour=start_dt.hour + 1)
    if start_dt <= datetime.utcnow():
        return jsonify({"error": "appointments must be in the future"}), 400

    conflict = TrainerAppointment.query.filter(
        TrainerAppointment.trainer_id == trainer_id,
        TrainerAppointment.status.in_(["pending", "confirmed", "completed"]),
        TrainerAppointment.start_at < end_dt,
        TrainerAppointment.end_at > start_dt,
    ).first()
    if conflict:
        return jsonify({"error": "trainer is unavailable for the selected time"}), 409

    appointment = TrainerAppointment(
        member_id=user_id,
        trainer_id=trainer_id,
        start_at=start_dt,
        end_at=end_dt,
        status="pending",
        notes=data.get("notes"),
    )
    db.session.add(appointment)
    db.session.commit()
    return jsonify(appointment.to_dict()), 201


@appointments_bp.get("/appointments/me")
@jwt_required()
def my_appointments():
    user_id = int(get_jwt_identity())
    appointments = TrainerAppointment.query.filter_by(member_id=user_id).order_by(TrainerAppointment.start_at.desc()).all()
    return jsonify([appointment.to_dict() for appointment in appointments])


@appointments_bp.patch("/appointments/<int:appointment_id>/cancel")
@jwt_required()
def cancel_appointment(appointment_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    appointment = TrainerAppointment.query.get_or_404(appointment_id)
    if claims.get("role") == "member" and appointment.member_id != user_id:
        return jsonify({"error": "you can only cancel your own appointment"}), 403
    if claims.get("role") == "trainer":
        trainer = Trainer.query.filter_by(user_id=user_id).first()
        if not trainer or appointment.trainer_id != trainer.id:
            return jsonify({"error": "you can only cancel appointments assigned to you"}), 403
    if claims.get("role") not in {"member", "admin", "trainer"}:
        return jsonify({"error": "unauthorized"}), 403
    appointment.status = "cancelled"
    db.session.commit()
    return jsonify(appointment.to_dict())


@appointments_bp.get("/trainer/appointments")
@jwt_required()
def trainer_appointments():
    claims = get_jwt()
    if claims.get("role") not in {"trainer", "admin"}:
        return jsonify({"error": "trainer access required"}), 403
    if claims.get("role") == "trainer":
        trainer = Trainer.query.filter_by(user_id=int(get_jwt_identity())).first()
        appointments = TrainerAppointment.query.filter_by(trainer_id=trainer.id).order_by(TrainerAppointment.start_at.desc()).all()
    else:
        appointments = TrainerAppointment.query.order_by(TrainerAppointment.start_at.desc()).all()
    return jsonify([appointment.to_dict() for appointment in appointments])


@appointments_bp.patch("/trainer/appointments/<int:appointment_id>/status")
@jwt_required()
def update_appointment_status(appointment_id):
    claims = get_jwt()
    if claims.get("role") not in {"trainer", "admin"}:
        return jsonify({"error": "trainer access required"}), 403
    appointment = TrainerAppointment.query.get_or_404(appointment_id)
    data = request.get_json() or {}
    new_status = data.get("status")
    if new_status not in {"pending", "confirmed", "cancelled", "rejected", "completed"}:
        return jsonify({"error": "invalid status"}), 400
    if claims.get("role") == "trainer":
        trainer = Trainer.query.filter_by(user_id=int(get_jwt_identity())).first()
        if not trainer or appointment.trainer_id != trainer.id:
            return jsonify({"error": "you can only manage appointments assigned to you"}), 403
    appointment.status = new_status
    db.session.commit()
    return jsonify(appointment.to_dict())


@appointments_bp.get("/admin/appointments")
@jwt_required()
def admin_appointments():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "admin access required"}), 403
    appointments = TrainerAppointment.query.order_by(TrainerAppointment.start_at.desc()).all()
    return jsonify([appointment.to_dict() for appointment in appointments])


@appointments_bp.get("/admin/appointments/summary")
@jwt_required()
def admin_appointment_summary():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "admin access required"}), 403
    total = db.session.query(func.count(TrainerAppointment.appointment_id)).scalar() or 0
    pending = db.session.query(func.count(TrainerAppointment.appointment_id)).filter(TrainerAppointment.status == "pending").scalar() or 0
    completed = db.session.query(func.count(TrainerAppointment.appointment_id)).filter(TrainerAppointment.status == "completed").scalar() or 0
    return jsonify({"total_appointments": total, "pending_appointments": pending, "completed_appointments": completed})
