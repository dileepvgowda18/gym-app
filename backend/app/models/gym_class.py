from app.extensions import db


class GymClass(db.Model):
    __tablename__ = "classes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey("trainers.id"), nullable=False)
    schedule_day = db.Column(db.String(20))  # e.g. Monday
    schedule_time = db.Column(db.String(20))  # e.g. "18:00"
    duration_minutes = db.Column(db.Integer, default=60)
    capacity = db.Column(db.Integer, default=20)
    description = db.Column(db.Text)

    bookings = db.relationship("Booking", backref="gym_class", lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_seats_left=True):
        data = {
            "id": self.id,
            "name": self.name,
            "trainer_id": self.trainer_id,
            "trainer_name": self.trainer.user.name if self.trainer and self.trainer.user else None,
            "schedule_day": self.schedule_day,
            "schedule_time": self.schedule_time,
            "duration_minutes": self.duration_minutes,
            "capacity": self.capacity,
            "description": self.description,
        }
        if include_seats_left:
            active_bookings = [b for b in self.bookings if b.status == "confirmed"]
            data["seats_left"] = max(self.capacity - len(active_bookings), 0)
        return data
