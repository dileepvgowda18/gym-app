"""
Seeds the database with demo data: an admin account, membership plans,
trainers and classes. Run with:  python seed.py
"""
from app import create_app
from app.extensions import db
from app.models import User, Plan, Trainer, GymClass

app = create_app()

with app.app_context():
    db.create_all()

    if not User.query.filter_by(email="admin@ironcore.gym").first():
        admin = User(name="Gym Admin", email="admin@ironcore.gym", role="admin", phone="9999999999")
        admin.set_password("admin123")
        db.session.add(admin)

    if Plan.query.count() == 0:
        db.session.add_all([
            Plan(name="Starter", price=999, duration_days=30,
                 features=["Gym floor access", "1 free trainer session", "Locker access"]),
            Plan(name="Pro", price=2499, duration_days=90,
                 features=["Everything in Starter", "All group classes", "Nutrition guide", "Guest passes x2"]),
            Plan(name="Elite", price=8999, duration_days=365,
                 features=["Everything in Pro", "Personal trainer x2/week", "Recovery lounge", "Priority booking"]),
        ])

    db.session.commit()

    if Trainer.query.count() == 0:
        trainer_data = [
            ("Riya Kapoor", "riya@ironcore.gym", "Strength & Conditioning", 6),
            ("Arjun Mehta", "arjun@ironcore.gym", "HIIT & Cardio", 4),
            ("Sana Iyer", "sana@ironcore.gym", "Yoga & Mobility", 8),
        ]
        trainers = []
        for name, email, spec, exp in trainer_data:
            u = User(name=name, email=email, role="trainer")
            u.set_password("trainer123")
            db.session.add(u)
            db.session.flush()
            t = Trainer(user_id=u.id, specialization=spec, years_experience=exp,
                        bio=f"{name} specializes in {spec.lower()} with {exp} years of coaching experience.")
            db.session.add(t)
            trainers.append(t)
        db.session.commit()

        db.session.add_all([
            GymClass(name="Morning Strength", trainer_id=trainers[0].id, schedule_day="Monday",
                      schedule_time="06:30", capacity=15, description="Full-body strength training to start the week."),
            GymClass(name="HIIT Blast", trainer_id=trainers[1].id, schedule_day="Tuesday",
                      schedule_time="18:00", capacity=20, description="High intensity interval training, all levels."),
            GymClass(name="Power Yoga", trainer_id=trainers[2].id, schedule_day="Wednesday",
                      schedule_time="07:00", capacity=12, description="Build flexibility and core strength."),
            GymClass(name="Evening Conditioning", trainer_id=trainers[0].id, schedule_day="Thursday",
                      schedule_time="19:00", capacity=15, description="Conditioning circuits for endurance."),
            GymClass(name="Cardio Burn", trainer_id=trainers[1].id, schedule_day="Friday",
                      schedule_time="17:30", capacity=20, description="Cardio-focused class to close the week."),
        ])
        db.session.commit()

    print("Seed complete.")
    print("Admin login -> email: admin@ironcore.gym  password: admin123")
