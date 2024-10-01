from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.order_model import Order, OrderUpdate

def create_order(session: Session, order_data: Order):
    session.add(order_data)
    session.commit()
    session.refresh(order_data)
    return order_data

def get_all_orders(session: Session):
    return session.exec(select(Order)).all()

def get_order_by_id(session: Session, order_id: int):
    return session.exec(select(Order).where(Order.id == order_id)).first()

def update_order_by_id(session: Session, order_id: int, order_update: OrderUpdate):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update only the fields that are provided in the request
    if order_update.user_id is not None:
        order.user_id = order_update.user_id
    if order_update.product_id is not None:
        order.product_id = order_update.product_id
    if order_update.quantity is not None:
        order.quantity = order_update.quantity
    if order_update.total_price is not None:
        order.total_price = order_update.total_price
    if order_update.status is not None:
        order.status = order_update.status

    session.add(order)
    session.commit()
    session.refresh(order)  # To return the updated order
    return order

def delete_order_by_id(session: Session, order_id: int):
    order = session.exec(select(Order).where(Order.id == order_id)).first()
    if order:
        session.delete(order)
        session.commit()
        return True
    return False

def track_order_by_id(session: Session, order_id: int):
    return session.exec(select(Order).where(Order.id == order_id)).first()