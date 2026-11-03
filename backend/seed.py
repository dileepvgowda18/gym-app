"""Seed demo data without duplicating production records."""
from datetime import datetime, timedelta

from app import create_app
from app.extensions import db
from app.models import Attendance, Booking, Exercise, GymClass, Plan, PlanExercise, Trainer, TrainerAppointment, User, WorkoutEntry, WorkoutPlan, WorkoutSession

app = create_app()

with app.app_context():
    db.create_all()

    if not User.query.filter_by(email="admin@ironcore.gym").first():
        admin = User(name="Gym Admin", email="admin@ironcore.gym", role="admin", phone="9999999999")
        admin.set_password("admin123")
        db.session.add(admin)

    member = User.query.filter_by(email="member@ironcore.gym").first()
    if not member:
        member = User(name="Aarav Sharma", email="member@ironcore.gym", role="member", phone="9876543210")
        member.set_password("member123")
        db.session.add(member)

    if Plan.query.count() == 0:
        db.session.add_all([
            Plan(name="Starter", price=999, duration_days=30, features=["Gym floor access", "1 free trainer session", "Locker access"]),
            Plan(name="Pro", price=2499, duration_days=90, features=["Everything in Starter", "All group classes", "Nutrition guide", "Guest passes x2"]),
            Plan(name="Elite", price=8999, duration_days=365, features=["Everything in Pro", "Personal trainer x2/week", "Recovery lounge", "Priority booking"]),
        ])

    trainer_users = []
    for name, email, spec, exp in [
        ("Riya Kapoor", "riya@ironcore.gym", "Strength & Conditioning", 6),
        ("Arjun Mehta", "arjun@ironcore.gym", "HIIT & Cardio", 4),
        ("Sana Iyer", "sana@ironcore.gym", "Yoga & Mobility", 8),
    ]:
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name=name, email=email, role="trainer")
            user.set_password("trainer123")
            db.session.add(user)
            db.session.flush()
        trainer = Trainer.query.filter_by(user_id=user.id).first()
        if not trainer:
            trainer = Trainer(user_id=user.id, specialization=spec, years_experience=exp, bio=f"{name} specializes in {spec.lower()} with {exp} years of coaching experience.")
            db.session.add(trainer)
            db.session.flush()
        trainer_users.append(trainer)

    if GymClass.query.count() == 0:
        db.session.add_all([
            GymClass(name="Morning Strength", trainer_id=trainer_users[0].id, schedule_day="Monday", schedule_time="06:30", capacity=15, description="Full-body strength training to start the week."),
            GymClass(name="HIIT Blast", trainer_id=trainer_users[1].id, schedule_day="Tuesday", schedule_time="18:00", capacity=20, description="High intensity interval training, all levels."),
            GymClass(name="Power Yoga", trainer_id=trainer_users[2].id, schedule_day="Wednesday", schedule_time="07:00", capacity=12, description="Build flexibility and core strength."),
            GymClass(name="Evening Conditioning", trainer_id=trainer_users[0].id, schedule_day="Thursday", schedule_time="19:00", capacity=15, description="Conditioning circuits for endurance."),
            GymClass(name="Cardio Burn", trainer_id=trainer_users[1].id, schedule_day="Friday", schedule_time="17:30", capacity=20, description="Cardio-focused class to close the week."),
        ])

    exercises = []
    for name, muscle_group, description in [
        ("Bench Press", "Chest", "Barbell press on a flat bench."),
        ("Squat", "Legs", "Compound lower body lift."),
        ("Dumbbell Curl", "Arms", "Biceps isolation exercise."),
        ("Deadlift", "Back", "Posterior chain strength movement."),
        ("Pull-Up", "Back", "Bodyweight vertical pulling exercise."),
    ]:
        exercise = Exercise.query.filter_by(exercise_name=name).first()
        if not exercise:
            exercise = Exercise(exercise_name=name, muscle_group=muscle_group, description=description)
            db.session.add(exercise)
            db.session.flush()
        exercises.append(exercise)

    if not Attendance.query.filter_by(member_id=member.id, check_out=None).first():
        now = datetime.utcnow()
        db.session.add(Attendance(member_id=member.id, check_in=now - timedelta(hours=2), check_out=now - timedelta(minutes=30)))
        db.session.add(Attendance(member_id=member.id, check_in=now - timedelta(days=1, hours=2), check_out=now - timedelta(days=1, hours=1)))

    if WorkoutSession.query.count() == 0:
        session = WorkoutSession(member_id=member.id, workout_date=datetime.utcnow().date(), notes="Upper body and legs focus.")
        db.session.add(session)
        db.session.flush()
        db.session.add_all([
            WorkoutEntry(session_id=session.session_id, exercise_id=exercises[0].exercise_id, sets=3, repetitions=12, weight_kg=40, notes="Strong effort"),
            WorkoutEntry(session_id=session.session_id, exercise_id=exercises[1].exercise_id, sets=3, repetitions=10, weight_kg=50, notes="Depth was solid"),
            WorkoutEntry(session_id=session.session_id, exercise_id=exercises[2].exercise_id, sets=3, repetitions=12, weight_kg=10, notes="Controlled tempo"),
        ])

    if WorkoutPlan.query.count() == 0:
        trainer = trainer_users[0]
        plan = WorkoutPlan(trainer_id=trainer.id, member_id=member.id, plan_name="Strength Foundation", description="Progressive overload plan")
        db.session.add(plan)
        db.session.flush()
        db.session.add_all([
            PlanExercise(plan_id=plan.plan_id, exercise_id=exercises[0].exercise_id, sets=4, repetitions=8, target_weight_kg=45),
            PlanExercise(plan_id=plan.plan_id, exercise_id=exercises[1].exercise_id, sets=4, repetitions=8, target_weight_kg=60),
        ])

    if TrainerAppointment.query.count() == 0:
        trainer = trainer_users[0]
        start = datetime.utcnow() + timedelta(days=1, hours=2)
        db.session.add(TrainerAppointment(member_id=member.id, trainer_id=trainer.id, start_at=start, end_at=start + timedelta(hours=1), status="pending", notes="Initial strength evaluation"))

    if not Booking.query.filter_by(user_id=member.id).first():
        gym_class = GymClass.query.order_by(GymClass.id.asc()).first()
        if gym_class:
            db.session.add(Booking(user_id=member.id, class_id=gym_class.id, status="confirmed"))

    db.session.commit()
    print("Seed complete.")
    print("Admin login -> email: admin@ironcore.gym  password: admin123")
    print("Member login -> email: member@ironcore.gym  password: member123")
