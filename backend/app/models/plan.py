from app.extensions import db


class Plan(db.Model):
    __tablename__ = "plans"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)  # e.g. 30, 90, 365
    features = db.Column(db.JSON, default=list)  # list of strings
    is_active = db.Column(db.Boolean, default=True)

    memberships = db.relationship("Membership", backref="plan", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": float(self.price),
            "duration_days": self.duration_days,
            "features": self.features or [],
            "is_active": self.is_active,
        }
