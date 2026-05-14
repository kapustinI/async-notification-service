from flask import Flask

from app.config import Config
from app.api import api_v1_bp
from app.extensions import db, celery

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    
    
    with app.app_context():
        from app import models  
        db.create_all()
        
    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"]
    )

    app.register_blueprint(api_v1_bp)

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200
    
    return app