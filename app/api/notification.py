from flask import Blueprint, jsonify, request
import json
from uuid import UUID
from app.extensions import db
from app.models import Notification
from app.utils.validators import validate_notification_payload
from datetime import datetime, timezone

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")

def log_event(event: str, **details) -> None:
    record = {
        "time": datetime.now(timezone.utc).isoformat(),
        "service": "api",
        "event": event,
        "details": details,
    }
    print(json.dumps(record, ensure_ascii=False), flush=True)

@notifications_bp.post("")
def create_notification():
    payload = request.get_json(silent=True) or {}
    log_event("notification_request_received", payload=payload)
    errors = validate_notification_payload(payload)
    if errors:
        log_event("notification_validation_failed", errors=errors)
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
    log_event("notification_saved", notification_id=str(notification.id), status=notification.status)

    from app.tasks import send_notification_task

    send_notification_task.delay(str(notification.id))
    log_event("notification_queued", notification_id=str(notification.id))

    return jsonify({"id": str(notification.id), "status": "queued"}), 201


@notifications_bp.get("/<notification_id>")
def get_notification(notification_id: str):
    try:
        notification_uuid = UUID(notification_id)
    except ValueError:
        log_event("notification_get_invalid_id", notification_id=notification_id)
        return jsonify({"error": "invalid notification id"}), 400
    
    notification = db.session.get(Notification, notification_uuid)
    if notification is None:
        log_event("notification_get_invalid_id", notification_id=notification_id)
        return jsonify({"error": "notification not found"}), 404
    
    log_event("notification_get_success", notification_id=str(notification.id), status=notification.status)
    
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

    log_event("notification_list_requested", status=status, limit=limit, offset=offset)

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

    log_event("notification_list_success", count=len(items))

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