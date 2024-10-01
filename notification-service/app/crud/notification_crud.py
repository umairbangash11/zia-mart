from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.notification_model import Notification, NotificationUpdate
from typing import List
from datetime import datetime

# Create Notification
def create_notification(notification: Notification, session: Session):
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification

# Get a single Notification by ID
def get_notification_by_id(notification_id: int, session: Session):
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

# Get all Notifications
def get_all_notifications(session: Session) -> List[Notification]:
    return session.exec(select(Notification)).all()

# Update a Notification by ID
def update_notification(notification_id: int, notification_data: NotificationUpdate, session: Session):
    notification = get_notification_by_id(notification_id, session)
    for key, value in notification_data.dict(exclude_unset=True).items():
        setattr(notification, key, value)
    notification.updated_at = datetime.utcnow()  # Update the timestamp
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification

# Delete a Notification by ID
def delete_notification(notification_id: int, session: Session):
    notification = get_notification_by_id(notification_id, session)
    session.delete(notification)
    session.commit()


#validate Notification by id 
def validate_notification(notification_id: int, session: Session):
    notification = get_notification_by_id(notification_id, session)
    if notification:
        return True
    return False