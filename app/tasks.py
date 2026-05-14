from app import create_app
from app.extensions import celery, db
from uuid import UUID
from app.models import Notification


flask_app = create_app()

celery.conf.update(
    broker_url=flask_app.config["CELERY_BROKER_URL"],
    result_backend=flask_app.config["CELERY_RESULT_BACKEND"],
)

@celery.task(name="app.tasks.send_notification_task")
def send_notification_task(notification_id: str) -> None:
    with flask_app.app_context():
        notification = Notification.query.get(UUID(notification_id))
        if  notification is None:
            print(f"[worker] notification not found: {notification_id}")
            return
        try:
            print(
                f"[worker] processing notification id={notification_id} "
                f"type={notification.type} recipient={notification.recipient}"
            )

            notification.status = "sent"
            notification.error_text = None

        except Exception as exc:
            notification.status = "failed"
            notification.error_text = str(exc)
            print(f"[worker] failed notification id={notification_id}: {exc}")

        finally:
            db.session.commit()