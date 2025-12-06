import os
from flask import Flask, jsonify
from config import Config
from extensions import db, migrate, jwt
from routes.auth import auth_bp
from routes.services import services_bp
from routes.bookings import bookings_bp
from routes.admin import admin_bp
from extensions import cors

def create_app(config_object=None):
    """App factory for the Flask application. Register extensions and blueprints here."""
    app = Flask(__name__)
    app.config.from_object(config_object or Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    # Enable CORS for the frontend (adjust origins as needed)
    cors.init_app(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})

    # Register routes/blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(services_bp, url_prefix='')
    app.register_blueprint(bookings_bp, url_prefix='/bookings')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'msg': 'Not Found', 'code': 404}), 404

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'msg': 'Bad Request', 'code': 400}), 400

    return app


if __name__ == '__main__':
    # Run development server when executed directly
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True)

# Notes:
# - Add new blueprints under `routes/` and register them in create_app.
# - Protect routes with `@jwt_required()` and check roles from `get_jwt()`.
