from flask import Flask, jsonify
from config import Config
from app.extensions import db, migrate, jwt, cors
from sqlalchemy.exc import SQLAlchemyError


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": app.config["CORS_ORIGINS"],
                "methods": ["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                "allow_headers": ["Authorization", "Content-Type"],
            }
        },
    )

    from app.routes.auth import auth_bp
    from app.routes.plans import plans_bp
    from app.routes.trainers import trainers_bp
    from app.routes.classes import classes_bp
    from app.routes.bookings import bookings_bp
    from app.routes.payments import payments_bp
    from app.routes.admin import admin_bp
    from app.routes.attendance import attendance_bp
    from app.routes.workouts import workouts_bp
    from app.routes.appointments import appointments_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(plans_bp)
    app.register_blueprint(trainers_bp)
    app.register_blueprint(classes_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(workouts_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(admin_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "internal server error"}), 500

    @app.errorhandler(SQLAlchemyError)
    def database_error(e):
        db.session.rollback()
        app.logger.exception("Database request failed")
        return jsonify({"error": "database request failed; check the database connection and schema"}), 500

    return app
