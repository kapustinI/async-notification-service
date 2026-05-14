import re
from typing import Any
from email_validator import EmailNotValidError, validate_email

ALLOWED_TYPES = {"email", "sms", "telegram"}
PHONE_PATTERN = re.compile(r"^\+\d{11}$")

def validate_notification_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    required_fields = ["type", "recipient", "message"]
    for field in required_fields:
        if not payload.get(field):
            errors.append(f"'{field}' is required")
    notif_type = payload.get("type")
    recipient = payload.get("recipient")
    channel_data = payload.get("channel_data")
    if notif_type and notif_type not in ALLOWED_TYPES:
        errors.append("'type' must be one of: email, sms, telegram")
    if notif_type == "email" and recipient:
        try:
            validate_email(recipient, check_deliverability=False)
        except EmailNotValidError:
            errors.append("'recipient' must be a valid email for type='email'")
    if notif_type in {"sms", "telegram"} and recipient:
        if not PHONE_PATTERN.match(recipient):
            errors.append("'recipient' must be a valid phone (e.g. +79524445566)")
    if channel_data is not None and not isinstance(channel_data, dict):
         errors.append("'channel_data' must be an object")
    return errors