from flask import Blueprint

from app.api.notification import notifications_bp

api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")
api_v1_bp.register_blueprint(notifications_bp)