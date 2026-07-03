from datetime import datetime
from app.extensions import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    membership_id = db.Column(db.Integer, db.ForeignKey("memberships.id"), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="completed")  # completed | pending | failed
    transaction_id = db.Column(db.String(80), unique=True)
    method = db.Column(db.String(30), default="card")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "membership_id": self.membership_id,
            "amount": float(self.amount),
            "payment_date": self.payment_date.isoformat(),
            "status": self.status,
            "transaction_id": self.transaction_id,
            "method": self.method,
        }
