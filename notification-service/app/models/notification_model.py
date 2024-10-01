from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    order_id: int
    type: str  # e.g., "email", "sms"
    status: str  # e.g., "pending", "sent", "failed"
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class NotificationUpdate(SQLModel):
    status: str | None = None
    updated_at: datetime | None = None
    message: str | None = None
    type: str | None= None
    user_id: int | None= None
    order_id: int | None= None
    

