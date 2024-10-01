from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class OrderBase(SQLModel):
    user_id: int
    product_id: int
    quantity: int
    total_price: float
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Order(OrderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class OrderResponse(OrderBase):
    id: int

class OrderUpdate(SQLModel):
    user_id: int | None = None
    product_id:int | None = None
    quantity:int | None = None
    total_price:float | None = None
    status:str | None = None

class OrderDelete(SQLModel):
    id: int