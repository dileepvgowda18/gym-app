from datetime import datetime

from app.extensions import db


class Exercise(db.Model):
    __tablename__ = "exercises"

    exercise_id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String(120), nullable=False, unique=True, index=True)
    muscle_group = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "exercise_id": self.exercise_id,
            "exercise_name": self.exercise_name,
            "muscle_group": self.muscle_group,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
