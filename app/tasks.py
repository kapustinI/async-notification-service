from app import create_app
from app.extensions import celery

flask_app = create_app()

celery.conf.update(
    broker_url=flask_app.config["CELERY_BROKER_URL"],
    result_backend=flask_app.config["CELERY_RESULT_BACKEND"],
)

@celery.task(name="app.tasks.ping")
def ping() -> str:
    return "pong"