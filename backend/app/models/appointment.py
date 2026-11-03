from datetime import datetime

from app.extensions import db


class TrainerAppointment(db.Model):
    __tablename__ = "trainer_appointments"

    appointment_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey("trainers.id"), nullable=False, index=True)
    start_at = db.Column(db.DateTime, nullable=False, index=True)
    end_at = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="pending", index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.CheckConstraint("end_at > start_at", name="appointment_end_after_start"),
        db.CheckConstraint("status IN ('pending','confirmed','cancelled','rejected','completed')", name="appointment_valid_status"),
    )

    def to_dict(self):
        return {
            "appointment_id": self.appointment_id,
            "member_id": self.member_id,
            "member_name": self.member.name if self.member else None,
            "trainer_id": self.trainer_id,
            "trainer_name": self.trainer.user.name if self.trainer and self.trainer.user else None,
            "trainer_specialization": self.trainer.specialization if self.trainer else None,
            "start_at": self.start_at.isoformat() if self.start_at else None,
            "end_at": self.end_at.isoformat() if self.end_at else None,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
