from app.models import Notification

def test_create_notif_success(client):
    payload = {
        "type": "email",
        "recipient": "test@mail.ru",
        "message": "testmess"
    }

    response = client.post("/api/v1/notifications", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["status"] == "queued"

def test_create_notif_valid_err(client):
    payload = {
        "type": "email",
        "recipient": "bad-mail0ru",
        "message": "testmess"
    }

    response = client.post("/api/v1/notifications", json=payload)

    assert response.status_code == 400
    data = response.get_json()
    assert "errors" in data
    
def test_get_notif_by_id(client, app):
    with app.app_context():
        temp = Notification(
            type="email",
            recipient = "test@mail.ru",
            message="testmess",
            status="pending",
        )
        from app.extensions import db
        db.session.add(temp)
        db.session.commit()
        notif_id = str(temp.id)
    response = client.get(f"/api/v1/notifications/{notif_id}")

    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == notif_id
    assert data["status"] == "pending"

def test_list_notif_with_STATUS_filter(client, app):
    with app.app_context():
        temp1 = Notification(
            type="email1",
            recipient = "test1@mail.ru",
            message="testmess1",
            status="sent",
        )
        temp2 = Notification(
            type="email2",
            recipient = "test2@mail.ru",
            message="testmess2",
            status="failed",
            error_text = "fail"
        )

        from app.extensions import db
        db.session.add(temp1)
        db.session.add(temp2)
        db.session.commit()

    response = client.get(f"/api/v1/notifications?status=failed")
    assert response.status_code == 200
    data = response.get_json()
    assert all(item["status"] == "failed" for item in data)
