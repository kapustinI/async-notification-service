import uuid
from datetime import datetime, timezone

from app.extensions import db


class Notification(db.Model):
    __tablename__ = "notification"

    id = db.Column(db.UUID(as_uuid = True), primary_key=True, default = uuid.uuid4)
    type = db.Column(db.String(20), nullable=False)
    recipient = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=True)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    error_text = db.Column(db.Text, nullable=True)
    channel_data = db.Column(db.JSON, nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "type": self.type,
            "recipient": self.recipient,
            "subject": self.subject,
            "message": self.message,
            "status": self.status,
            "error": self.error_text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "channel_data": self.channel_data,
        }
