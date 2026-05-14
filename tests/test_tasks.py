from uuid import UUID
from app.extensions import db
from app.models import Notification
from app.tasks import send_notification_task

def test_send_notification_task(app):
    with app.app_context():
        temp = Notification(
            type="email",
            recipient="user@example.com",
            message="hello",
            status="pending",
        )
        db.session.add(temp)
        db.session.commit()
        notification_id = str(temp.id)

    send_notification_task(notification_id)

    with app.app_context():
        updated = db.session.get(Notification, UUID(notification_id))
        assert updated is not None
        assert updated.status == "sent"
        assert updated.error_text is None