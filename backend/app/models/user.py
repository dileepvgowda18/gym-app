from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False, default="member")  # member | trainer | admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    memberships = db.relationship("Membership", backref="user", lazy=True, cascade="all, delete-orphan")
    bookings = db.relationship("Booking", backref="user", lazy=True, cascade="all, delete-orphan")
    payments = db.relationship("Payment", backref="user", lazy=True, cascade="all, delete-orphan")
    trainer_profile = db.relationship("Trainer", backref="user", uselist=False, cascade="all, delete-orphan")
    attendance_records = db.relationship("Attendance", foreign_keys="Attendance.member_id", backref="member", lazy=True, cascade="all, delete-orphan")
    workout_sessions = db.relationship("WorkoutSession", foreign_keys="WorkoutSession.member_id", backref="member", lazy=True, cascade="all, delete-orphan")
    workout_plans = db.relationship("WorkoutPlan", foreign_keys="WorkoutPlan.member_id", backref="member", lazy=True, cascade="all, delete-orphan")
    member_appointments = db.relationship("TrainerAppointment", foreign_keys="TrainerAppointment.member_id", backref="member", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
