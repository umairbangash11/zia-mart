from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    order_id: int
    amount: float
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TransactionUpdate(SQLModel):
    user_id: Optional[int] = None
    order_id: Optional[int] = None
    amount: float | None = None
    status: Optional[str] | None = None

class TransactionDelete(SQLModel):
    id: int