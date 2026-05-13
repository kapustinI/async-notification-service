from app.utils.validators import validate_notification_payload


def test_valid_payload_email_ok():
    payload = {
        "type": "email",
        "recipient": "user@mail.ru",
        "message": "hello",
    }
    errors = validate_notification_payload(payload)

    assert errors == []

def test_valid_payload_email_bad():
    payload = {
        "type": "email",
        "recipient": "badmail.ru",
        "message": "hello",
    }
    errors = validate_notification_payload(payload)

    assert "'recipient' must be a valid email for type='email'" in errors

def test_validate_payload_sms_ok():
    payload = {
        "type": "sms",
        "recipient": "+79991234567",
        "message": "hello",
    }

    errors = validate_notification_payload(payload)

    assert errors == []

def test_validate_payload_sms_invalid_phone():
    payload = {
        "type": "sms",
        "recipient": "7999",
        "message": "hello",
    }

    errors = validate_notification_payload(payload)

    assert "'recipient' must be a valid phone (e.g. +79524445566)" in errors

def test_invalid_type():
    payload = {
        "type": "push",
        "recipient": "user@mail.ru",
        "message": "hello",
    }

    errors = validate_notification_payload(payload)

    assert "'type' must be one of: email, sms, telegram" in errors
    
def test_missing_required_field_message():
    payload = {
        "type": "email",
        "recipient": "user@mail.ru",
    }

    errors = validate_notification_payload(payload)

    assert "'message' is required" in errors