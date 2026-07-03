from datetime import datetime
from app.extensions import db


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="confirmed")  # confirmed | cancelled

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "member_name": self.user.name if self.user else None,
            "class": self.gym_class.to_dict(include_seats_left=False) if self.gym_class else None,
            "booking_date": self.booking_date.isoformat(),
            "status": self.status,
        }
