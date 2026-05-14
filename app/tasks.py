from app import create_app
from app.extensions import celery, db
from uuid import UUID
from app.models import Notification
import json
from datetime import datetime, timezone

flask_app = create_app()

celery.conf.update(
    broker_url=flask_app.config["CELERY_BROKER_URL"],
    result_backend=flask_app.config["CELERY_RESULT_BACKEND"],
)

def log_event(event: str, **details) -> None:
    record = {
        "time": datetime.now(timezone.utc).isoformat(),
        "service": "worker",
        "event": event,
        "details": details,
    }
    print(json.dumps(record, ensure_ascii=False), flush=True)

@celery.task(name="app.tasks.send_notification_task")
def send_notification_task(notification_id: str) -> None:
    with flask_app.app_context():
        log_event("notification_processing_started", notification_id=notification_id)
        notification = db.session.get(Notification, UUID(notification_id))
        if  notification is None:
            log_event("notification_not_found", notification_id=notification_id)
            return
        try:
            notification.status = "sent"
            notification.error_text = None
            log_event("notification_processing_succeeded", notification_id=notification_id, status="sent")

        except Exception as exc:
            notification.status = "failed"
            notification.error_text = str(exc)
            log_event("notification_processing_failed", notification_id=notification_id, error=str(exc))

        finally:
            db.session.commit()