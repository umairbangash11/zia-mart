# main.py
from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json
from app import settings
from app.db_engine import engine
from app.models.order_model import Order, OrderResponse,OrderUpdate
from app.crud.order_crud import (create_order, get_all_orders, get_order_by_id, delete_order_by_id, update_order_by_id)
from app.deps import get_session, get_kafka_producer
from app.consumers.order_consumer import consume_messages
from datetime import datetime
# from app.consumers.notification_consumer import consume_notification_messages
#from app.consumers.order_payment_consumer import consume_order_payment_messages
# from app.hello_ai import chat_completion



def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating ... ... ?? !!!! ")

    task = asyncio.create_task(consume_messages(
       settings.KAFKA_ORDER_TOPIC, 'broker:19092'))
    
    # asyncio.create_task(consume_notification_messages(
    #     "notification-event",
    #     #settings.KAFKA_INVENTORY_TOPIC,
    #     'broker:19092'
        
    # ))
    
    # asyncio.create_task(consume_order_payment_messages(
    #     "transaction-event",
    #     #settings.KAFKA_INVENTORY_TOPIC,
    #     'broker:19092'
        
    # ))


    create_db_and_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Hello World API with DB",
    version="0.0.1",
)

@app.get("/")
def read_root():
    return {"Hello": "Order Service"}

@app.post("/manage-orders/", response_model=OrderResponse)
async def create_new_order(order: Order,
    session: Annotated[Session, Depends(get_session)], 
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    """ Create a new order and send it to Kafka"""

    # Convert the order to a dictionary and handle datetime fields
    order_dict = {
        field: (getattr(order, field).isoformat() if isinstance(getattr(order, field), datetime) else getattr(order, field))
        for field in order.dict()
    }
    
    # Convert to JSON
    order_json = json.dumps(order_dict).encode("utf-8")
    print("order_JSON:", order_json)
    
    # Produce message
    await producer.send_and_wait(settings.KAFKA_ORDER_TOPIC, order_json)
   
    return order

@app.get("/manage-orders/", response_model=list[OrderResponse])
def get_orders(session: Annotated[Session, Depends(get_session)]):
    orders = get_all_orders(session=session)
    return orders

@app.get("/manage-orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, session: Annotated[Session, Depends(get_session)]):
    order = get_order_by_id(session=session, order_id=order_id)

    try:
        return get_order_by_id(order_id=order_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/manage-orders/{order_id}", response_model=OrderResponse)
async def update_single_order(
    order_id: int,
    order_update: OrderUpdate,  # The data for the order update
    session: Annotated[Session, Depends(get_session)],  # Database session dependency
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]  # Kafka producer dependency
):
    """ Update a single order by ID and send a message to Kafka """
    try:
        # Update the order by passing the order_update object to the CRUD function
        updated_order = update_order_by_id(
            session=session, 
            order_id=order_id, 
            order_update=order_update  # This will update the fields based on provided values
        )
        
        if not updated_order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Prepare the Kafka message with all updated data
        order_dict = {
            "order_id": order_id, 
            "action": "update", 
            "updated_data": {
                "user_id": order_update.user_id,
                "product_id": order_update.product_id,
                "quantity": order_update.quantity,
                "total_price": order_update.total_price,
                "status": order_update.status
            }
        }
        order_json = json.dumps(order_dict).encode("utf-8")
        print("order_JSON:", order_json)

        # Send the Kafka message
        await producer.send_and_wait(topic="order-events", value=order_json)

        # Return the updated order
        return updated_order

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
  
@app.delete("/manage-orders/{order_id}", response_model=dict)
async def delete_single_order(
    order_id: int,
    session: Annotated[Session, Depends(get_session)],
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
):
    """ Delete a single order by ID and send a message to Kafka"""

    try:
        # Check if the order exists before attempting to delete
        order = get_order_by_id(session=session, order_id=order_id)  # Add this check
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Proceed to delete the order
        delete_order_by_id(session=session, order_id=order_id)  # Perform the actual deletion

        # Prepare the Kafka message
        order_dict = {"order_id": order_id, "action": "delete"}
        order_json = json.dumps(order_dict).encode("utf-8")
        print("order_JSON:", order_json)

        # Produce message to Kafka
        await producer.send_and_wait("order-events", order_json)

        # Return a confirmation message
        return {"message": f"Order with ID {order_id} successfully deleted."}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
@app.get("/track-order", response_model=OrderResponse)
def get_order(order_id: int, session: Annotated[Session, Depends(get_session)]):
    order = get_order_by_id(session=session, order_id=order_id)
    return order

@app.get("/hello-ai")
def get_ai_response(prompt:str):
    return chat_completion(prompt)