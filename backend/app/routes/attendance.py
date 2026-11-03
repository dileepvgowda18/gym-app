from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models import Attendance, User

attendance_bp = Blueprint("attendance", __name__, url_prefix="/api")


@attendance_bp.post("/attendance/check-in")
@jwt_required()
def check_in():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get("role") != "member":
        return jsonify({"error": "only members can check in"}), 403

    existing = Attendance.query.filter_by(member_id=user_id, check_out=None).first()
    if existing:
        return jsonify({"error": "member is already checked in"}), 409

    record = Attendance(member_id=user_id, check_in=datetime.utcnow())
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


@attendance_bp.post("/attendance/check-out")
@jwt_required()
def check_out():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get("role") != "member":
        return jsonify({"error": "only members can check out"}), 403

    record = Attendance.query.filter_by(member_id=user_id, check_out=None).order_by(Attendance.check_in.desc()).first()
    if not record:
        return jsonify({"error": "no active check-in found"}), 400

    record.check_out = datetime.utcnow()
    db.session.commit()
    return jsonify(record.to_dict())


@attendance_bp.get("/attendance/me")
@jwt_required()
def my_attendance():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get("role") not in {"member", "admin"}:
        return jsonify({"error": "unauthorized"}), 403

    records = Attendance.query.filter_by(member_id=user_id).order_by(Attendance.check_in.desc()).all()
    current = Attendance.query.filter_by(member_id=user_id, check_out=None).first()
    total_visits = Attendance.query.filter_by(member_id=user_id).count()
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    monthly_visits = db.session.query(func.count(Attendance.attendance_id)).filter(
        Attendance.member_id == user_id,
        func.extract("month", Attendance.check_in) == current_month,
        func.extract("year", Attendance.check_in) == current_year,
    ).scalar() or 0

    return jsonify({
        "current_status": "checked_in" if current else "checked_out",
        "total_visits": total_visits,
        "monthly_visits": monthly_visits,
        "records": [r.to_dict() for r in records],
    })


@attendance_bp.get("/admin/attendance")
@jwt_required()
def admin_attendance_list():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "admin access required"}), 403

    member_id = request.args.get("member_id", type=int)
    date_filter = request.args.get("date")
    query = Attendance.query.join(User)
    if member_id:
        query = query.filter(Attendance.member_id == member_id)
    if date_filter:
        query = query.filter(func.date(Attendance.check_in) == date_filter)

    records = query.order_by(Attendance.check_in.desc()).all()
    return jsonify([r.to_dict() for r in records])


@attendance_bp.get("/admin/attendance/summary")
@jwt_required()
def admin_attendance_summary():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "admin access required"}), 403

    today = datetime.utcnow().date()
    total_visits = db.session.query(func.count(Attendance.attendance_id)).scalar() or 0
    checked_in_now = db.session.query(func.count(Attendance.attendance_id)).filter(Attendance.check_out.is_(None)).scalar() or 0
    daily_total = db.session.query(func.count(Attendance.attendance_id)).filter(func.date(Attendance.check_in) == today).scalar() or 0
    monthly_total = db.session.query(func.count(Attendance.attendance_id)).filter(
        func.extract("month", Attendance.check_in) == datetime.utcnow().month,
        func.extract("year", Attendance.check_in) == datetime.utcnow().year,
    ).scalar() or 0
    active_members = db.session.query(func.count(func.distinct(Attendance.member_id))).filter(Attendance.check_out.is_(None)).scalar() or 0

    return jsonify({
        "total_visits": total_visits,
        "checked_in_now": checked_in_now,
        "daily_attendance": daily_total,
        "monthly_attendance": monthly_total,
        "members_currently_in_gym": active_members,
    })
