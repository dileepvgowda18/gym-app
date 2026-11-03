from app.extensions import db


class Trainer(db.Model):
    __tablename__ = "trainers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    specialization = db.Column(db.String(120))
    bio = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    years_experience = db.Column(db.Integer, default=0)

    classes = db.relationship("GymClass", backref="trainer", lazy=True)
    appointments = db.relationship("TrainerAppointment", foreign_keys="TrainerAppointment.trainer_id", backref="trainer", lazy=True, cascade="all, delete-orphan")
    workout_plans = db.relationship("WorkoutPlan", foreign_keys="WorkoutPlan.trainer_id", backref="trainer", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.user.name if self.user else None,
            "email": self.user.email if self.user else None,
            "specialization": self.specialization,
            "bio": self.bio,
            "image_url": self.image_url,
            "years_experience": self.years_experience,
        }
