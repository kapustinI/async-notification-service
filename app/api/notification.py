from flask import Blueprint, jsonify, request

from uuid import UUID
from app.extensions import db
from app.models import Notification
from app.utils.validators import validate_notification_payload

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")

@notifications_bp.post("")
def create_notification():
    payload = request.get_json(silent=True) or {}
    errors = validate_notification_payload(payload)
    if errors:
        return jsonify({"errors": errors})
    
    notification = Notification(
        type = payload["type"],
        recipient=payload["recipient"],
        subject=payload.get("subject"),
        channel_data=payload.get("channel_data"),
        message=payload["message"],
        status="pending",
    )

    db.session.add(notification)
    db.session.commit()

    from app.tasks import send_notification_task

    send_notification_task.delay(str(notification.id))

    return jsonify({"id": str(notification.id), "status": "queued"}), 201


@notifications_bp.get("/<notification_id>")
def get_notification(notification_id: str):
    try:
        notification_uuid = UUID(notification_id)
    except ValueError:
        return jsonify({"error": "invalid notification id"}), 400
    
    notification = Notification.query.get(notification_uuid)
    if notification is None:
        return jsonify({"error": "notification not found"}), 404
    
    return (
        jsonify(
            {
                "id": str(notification.id),
                "status": notification.status,
                "error": notification.error_text,
            }
        ),
        200
    )