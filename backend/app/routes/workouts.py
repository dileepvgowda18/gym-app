from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models import Exercise, Trainer, WorkoutEntry, WorkoutPlan, WorkoutSession, PlanExercise

workouts_bp = Blueprint("workouts", __name__, url_prefix="/api")


@workouts_bp.get("/exercises")
@jwt_required()
def list_exercises():
    exercises = Exercise.query.order_by(Exercise.exercise_name.asc()).all()
    return jsonify([exercise.to_dict() for exercise in exercises])


@workouts_bp.post("/workouts")
@jwt_required()
def create_workout_session():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get("role") not in {"member", "admin"}:
        return jsonify({"error": "member access required"}), 403

    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "request body must be a JSON object"}), 400
    member_id = user_id if claims.get("role") == "member" else data.get("member_id", user_id)
    entries = data.get("entries", [])
    if not entries:
        return jsonify({"error": "at least one exercise entry is required"}), 400

    workout_date = data.get("workout_date")
    if workout_date:
        try:
            parsed_workout_date = date.fromisoformat(workout_date)
        except (TypeError, ValueError):
            return jsonify({"error": "workout_date must use YYYY-MM-DD format"}), 400
        if parsed_workout_date.isoformat() != workout_date:
            return jsonify({"error": "workout_date must use YYYY-MM-DD format"}), 400
        workout_date = parsed_workout_date
    else:
        workout_date = date.today()

    session = WorkoutSession(member_id=member_id, workout_date=workout_date, notes=data.get("notes"))
    db.session.add(session)
    db.session.flush()

    for item in entries:
        if not isinstance(item, dict):
            return jsonify({"error": "invalid workout entry"}), 400
        exercise_id = item.get("exercise_id")
        sets = item.get("sets")
        reps = item.get("repetitions")
        weight = item.get("weight_kg", 0)
        if exercise_id is None or sets is None or reps is None:
            return jsonify({"error": "exercise_id, sets and repetitions are required"}), 400
        entry = WorkoutEntry(
            session_id=session.session_id,
            exercise_id=exercise_id,
            sets=sets,
            repetitions=reps,
            weight_kg=weight,
            notes=item.get("notes"),
        )
        db.session.add(entry)

    db.session.commit()
    return jsonify(session.to_dict()), 201


@workouts_bp.get("/workouts/me")
@jwt_required()
def list_my_workouts():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get("role") == "admin":
        sessions = WorkoutSession.query.order_by(WorkoutSession.workout_date.desc()).all()
    else:
        sessions = WorkoutSession.query.filter_by(member_id=user_id).order_by(WorkoutSession.workout_date.desc()).all()
    return jsonify([session.to_dict() for session in sessions])


@workouts_bp.put("/workouts/<int:session_id>")
@jwt_required()
def update_workout_session(session_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    session = WorkoutSession.query.get_or_404(session_id)
    if claims.get("role") == "member" and session.member_id != user_id:
        return jsonify({"error": "you can only modify your own workout records"}), 403
    if claims.get("role") == "trainer":
        return jsonify({"error": "trainers cannot update member workouts directly"}), 403

    data = request.get_json() or {}
    if "notes" in data:
        session.notes = data["notes"]
    if "workout_date" in data:
        try:
            workout_date = date.fromisoformat(data["workout_date"])
        except (TypeError, ValueError):
            return jsonify({"error": "workout_date must use YYYY-MM-DD format"}), 400
        if workout_date.isoformat() != data["workout_date"]:
            return jsonify({"error": "workout_date must use YYYY-MM-DD format"}), 400
        session.workout_date = workout_date
    if "entries" in data:
        for existing_entry in list(session.entries):
            db.session.delete(existing_entry)
        for item in data["entries"]:
            db.session.add(WorkoutEntry(
                session_id=session.session_id,
                exercise_id=item["exercise_id"],
                sets=item["sets"],
                repetitions=item["repetitions"],
                weight_kg=item.get("weight_kg", 0),
                notes=item.get("notes"),
            ))

    db.session.commit()
    return jsonify(session.to_dict())


@workouts_bp.delete("/workouts/<int:session_id>")
@jwt_required()
def delete_workout_session(session_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    session = WorkoutSession.query.get_or_404(session_id)
    if claims.get("role") == "member" and session.member_id != user_id:
        return jsonify({"error": "you can only delete your own workout records"}), 403
    if claims.get("role") == "trainer":
        return jsonify({"error": "trainers cannot delete member workouts"}), 403
    db.session.delete(session)
    db.session.commit()
    return jsonify({"message": "workout deleted"})


@workouts_bp.get("/trainer/workout-plans")
@jwt_required()
def trainer_workout_plans():
    claims = get_jwt()
    if claims.get("role") not in {"trainer", "admin"}:
        return jsonify({"error": "trainer access required"}), 403
    if claims.get("role") == "admin":
        plans = WorkoutPlan.query.order_by(WorkoutPlan.created_at.desc()).all()
    else:
        trainer = Trainer.query.filter_by(user_id=int(get_jwt_identity())).first()
        if not trainer:
            return jsonify({"error": "trainer profile not found"}), 404
        plans = WorkoutPlan.query.filter_by(trainer_id=trainer.id).order_by(WorkoutPlan.created_at.desc()).all()
    return jsonify([plan.to_dict() for plan in plans])


@workouts_bp.post("/workout-plans")
@jwt_required()
def create_workout_plan():
    claims = get_jwt()
    if claims.get("role") not in {"trainer", "admin"}:
        return jsonify({"error": "trainer access required"}), 403

    data = request.get_json() or {}
    trainer_id = data.get("trainer_id")
    member_id = data.get("member_id")
    if not trainer_id or not member_id:
        return jsonify({"error": "trainer_id and member_id are required"}), 400

    trainer_profile = Trainer.query.get(trainer_id)
    if not trainer_profile:
        return jsonify({"error": "trainer not found"}), 404

    if claims.get("role") == "trainer":
        current_trainer = Trainer.query.filter_by(user_id=int(get_jwt_identity())).first()
        if current_trainer and trainer_id != current_trainer.id:
            return jsonify({"error": "you can only assign plans to your own members"}), 403

    plan = WorkoutPlan(
        trainer_id=trainer_id,
        member_id=member_id,
        plan_name=data.get("plan_name") or "Workout Plan",
        description=data.get("description"),
    )
    db.session.add(plan)
    db.session.flush()

    for item in data.get("exercises", []):
        db.session.add(PlanExercise(
            plan_id=plan.plan_id,
            exercise_id=item["exercise_id"],
            sets=item["sets"],
            repetitions=item["repetitions"],
            target_weight_kg=item.get("target_weight_kg", 0),
        ))

    db.session.commit()
    return jsonify(plan.to_dict()), 201


@workouts_bp.get("/admin/workout-summary")
@jwt_required()
def admin_workout_summary():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "admin access required"}), 403

    summary = {
        "total_workout_sessions": db.session.query(func.count(WorkoutSession.session_id)).scalar() or 0,
        "total_exercises": db.session.query(func.count(Exercise.exercise_id)).scalar() or 0,
        "total_workout_plans": db.session.query(func.count(WorkoutPlan.plan_id)).scalar() or 0,
    }
    return jsonify(summary)
