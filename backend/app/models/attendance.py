from datetime import datetime
from zoneinfo import ZoneInfo

from app.extensions import db

IST = ZoneInfo("Asia/Kolkata")


class Attendance(db.Model):
    __tablename__ = "attendance"

    attendance_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    check_in = db.Column(db.DateTime, nullable=False, index=True)
    check_out = db.Column(db.DateTime, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.Index("idx_attendance_member_checkin", "member_id", "check_in"),
    )

    @staticmethod
    def _format_ist(value):
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=IST)
        return value.astimezone(IST).isoformat()

    @property
    def duration_minutes(self):
        if self.check_in and self.check_out:
            delta = self.check_out - self.check_in
            return max(int(delta.total_seconds() // 60), 0)
        return 0

    def to_dict(self):
        return {
            "attendance_id": self.attendance_id,
            "member_id": self.member_id,
            "member_name": self.member.name if self.member else None,
            "check_in": self._format_ist(self.check_in),
            "check_out": self._format_ist(self.check_out),
            "created_at": self._format_ist(self.created_at),
            "duration_minutes": self.duration_minutes,
        }
