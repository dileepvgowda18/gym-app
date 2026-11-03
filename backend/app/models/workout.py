from datetime import datetime, date

from app.extensions import db


class WorkoutSession(db.Model):
    __tablename__ = "workout_sessions"

    session_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    workout_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    entries = db.relationship("WorkoutEntry", backref="session", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "member_id": self.member_id,
            "member_name": self.member.name if self.member else None,
            "workout_date": self.workout_date.isoformat() if self.workout_date else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "entries": [e.to_dict() for e in self.entries],
        }


class WorkoutEntry(db.Model):
    __tablename__ = "workout_entries"

    entry_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("workout_sessions.session_id"), nullable=False, index=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.exercise_id"), nullable=False, index=True)
    sets = db.Column(db.Integer, nullable=False)
    repetitions = db.Column(db.Integer, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False, default=0.0)
    notes = db.Column(db.Text)
    exercise = db.relationship("Exercise", backref="workout_entries", lazy=True)

    __table_args__ = (
        db.CheckConstraint("sets > 0", name="workout_entry_sets_positive"),
        db.CheckConstraint("repetitions > 0", name="workout_entry_repetitions_positive"),
        db.CheckConstraint("weight_kg >= 0", name="workout_entry_weight_non_negative"),
    )

    def to_dict(self):
        return {
            "entry_id": self.entry_id,
            "session_id": self.session_id,
            "exercise_id": self.exercise_id,
            "exercise_name": self.exercise.exercise_name if self.exercise else None,
            "sets": self.sets,
            "repetitions": self.repetitions,
            "weight_kg": float(self.weight_kg),
            "notes": self.notes,
        }


class WorkoutPlan(db.Model):
    __tablename__ = "workout_plans"

    plan_id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey("trainers.id"), nullable=False, index=True)
    member_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    plan_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    exercises = db.relationship("PlanExercise", backref="plan", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "plan_id": self.plan_id,
            "trainer_id": self.trainer_id,
            "trainer_name": self.trainer.user.name if self.trainer and self.trainer.user else None,
            "member_id": self.member_id,
            "member_name": self.member.name if self.member else None,
            "plan_name": self.plan_name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "exercises": [e.to_dict() for e in self.exercises],
        }


class PlanExercise(db.Model):
    __tablename__ = "plan_exercises"

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("workout_plans.plan_id"), nullable=False, index=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.exercise_id"), nullable=False, index=True)
    sets = db.Column(db.Integer, nullable=False)
    repetitions = db.Column(db.Integer, nullable=False)
    target_weight_kg = db.Column(db.Float, nullable=False, default=0.0)
    exercise = db.relationship("Exercise", backref="plan_exercises", lazy=True)

    __table_args__ = (
        db.CheckConstraint("sets > 0", name="plan_exercise_sets_positive"),
        db.CheckConstraint("repetitions > 0", name="plan_exercise_repetitions_positive"),
        db.CheckConstraint("target_weight_kg >= 0", name="plan_exercise_target_weight_non_negative"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "plan_id": self.plan_id,
            "exercise_id": self.exercise_id,
            "exercise_name": self.exercise.exercise_name if self.exercise else None,
            "sets": self.sets,
            "repetitions": self.repetitions,
            "target_weight_kg": float(self.target_weight_kg),
        }
