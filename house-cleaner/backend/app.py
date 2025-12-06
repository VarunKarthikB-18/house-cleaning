import os
import re
from flask import Flask, jsonify, request
from config import Config
from extensions import db, migrate, jwt
from routes.auth import auth_bp
from routes.services import services_bp
from routes.bookings import bookings_bp
from routes.admin import admin_bp
from routes.reviews import reviews_bp
from extensions import cors

def create_app(config_object=None):
    """App factory for the Flask application. Register extensions and blueprints here."""
    app = Flask(__name__)
    app.config.from_object(config_object or Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    # Enable CORS for the frontend (allow all localhost ports for development)
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify({})
            origin = request.headers.get('Origin', '')
            if re.match(r'http://(localhost|127\.0\.0\.1):\d+', origin):
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
    
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin', '')
        # Allow all localhost and 127.0.0.1 origins for development
        if re.match(r'http://(localhost|127\.0\.0\.1):\d+', origin):
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    # Register routes/blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(services_bp, url_prefix='')
    app.register_blueprint(bookings_bp, url_prefix='/bookings')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(reviews_bp, url_prefix='')

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
    # Use port 5001 to avoid conflicts with AirPlay Receiver on macOS
    port = int(os.environ.get('FLASK_PORT', 5001))
    app.run(host='127.0.0.1', port=port, debug=True)

# Notes:
# - Add new blueprints under `routes/` and register them in create_app.
# - Protect routes with `@jwt_required()` and check roles from `get_jwt()`.
