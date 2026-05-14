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
        return jsonify({"errors": errors}), 400
    
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

@notifications_bp.get("")
def list_notifications():
    status = request.args.get("status")
    limit = request.args.get("limit", default=20, type=int)
    offset = request.args.get("offset", default=0, type=int)

    print("raw args:", request.args)
    print("parsed:", status, limit, offset)

    if limit is None or limit <= 0:
        return jsonify({"error": "'limit' must be positive integer"}), 400
    if offset is None or offset < 0:
        return jsonify({"error": "'offset' must be a non-negative integer"}), 400
    
    query = Notification.query

    if status:
        allowed_status = {"pending", "sent", "failed"}
        if status not in allowed_status:
            return jsonify({"error": "'status' must be one of: pending, sent, failed"}), 400
        query = query.filter_by(status=status)
    
    items = (
        query.order_by(Notification.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return (
        jsonify(
            [
                {
                    "id": str(item.id),
                    "status": item.status,
                    "error": item.error_text,

                }
                 for item in items
            ]
        ),
        200,
    )