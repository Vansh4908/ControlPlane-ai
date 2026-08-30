from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.database.connection import db
from app.api.routes.applications import applications_bp
from app.api.routes.policies import policies_bp
from app.api.routes.evaluation import evaluation_bp
from app.api.routes.review import review_bp
from app.api.routes.knowledge import knowledge_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    db.init_app(app)

    app.register_blueprint(applications_bp)
    app.register_blueprint(policies_bp)
    app.register_blueprint(evaluation_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(knowledge_bp)

    return app