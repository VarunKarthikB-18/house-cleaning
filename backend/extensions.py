from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialize extensions here (to be initialized with app in create_app)
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
