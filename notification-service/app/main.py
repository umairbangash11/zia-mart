from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, SQLModel
from app.crud.notification_crud import (
    create_notification, 
    get_notification_by_id, 
    get_all_notifications, 
    update_notification, 
    delete_notification,
    validate_notification
)
from datetime import datetime
from app.models.notification_model import Notification, NotificationUpdate
from app.deps import get_session, get_kafka_producer
from app.db_engine import engine
from aiokafka import AIOKafkaProducer
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Annotated
import asyncio
import json
from typing import List
from app import settings
from app.consumers.notification_consumer import consume_messages
# from app.consumers.add_user_consumer import consume_user_messages

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    
    task = asyncio.create_task(consume_messages(
        settings.KAFKA_NOTIFICATION_TOPIC, 'broker:19092'))
    
    # asyncio.create_task(consume_user_messages(
    #     topic="user-events",
    #     bootstrap_servers='broker:19092'
    # ))

    
    create_db_and_tables()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Notification Service API",
    version="0.0.1",
)

@app.get("/")
def read_root():
    return {"Hello": "Notification Service"}

@app.post("/manage-notifications/", response_model=Notification)
async def create_notification(
    notification: Notification, session: Annotated[Session, Depends(get_session)],
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
   
):
    # Convert notification object to dict and then to JSON
    notification_dict = {field: getattr(notification, field) for field in notification.dict()}
    notification_json = json.dumps(notification_dict).encode("utf-8")
    print("notification_JSON:", notification_json)

    # Asynchronously send notification to Kafka topic
    await producer.send_and_wait("notification-event", notification_json)
    return notification

@app.get("/manage-notifications/", response_model=List[Notification])
def get_all_notifications_route(session: Annotated[Session, Depends(get_session)]):

    return get_all_notifications(session)


@app.get("/manage-notification/{notification_id}", response_model=Notification)
def get_single_notification_route(
    notification_id: int, 
    session: Annotated[Session, Depends(get_session)]
):
    """ Get a single notification by ID"""
    notification = get_notification_by_id(notification_id=notification_id, session=session)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@app.patch("/manage-notification/{notification_id}", response_model=Notification)
async def update_single_notification_route(
    notification_id: int,
    notification_update: NotificationUpdate,  # Keep the argument name as it is in the route
    session: Annotated[Session, Depends(get_session)],
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
):
    """ Update a single notification by ID and send a message to Kafka"""
    
    # Correct the argument passed to match the function definition
    updated_notification = update_notification(
        notification_id=notification_id, 
        notification_data=notification_update,  # Rename this to match the expected parameter in update_notification()
        session=session
    )
    
    if not updated_notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    # Convert any datetime fields in updated_notification to strings
    updated_data = updated_notification.dict()
    
    for key, value in updated_data.items():
        if isinstance(value, datetime):
            updated_data[key] = value.strftime("%Y-%m-%d %H:%M:%S")  # Format as needed

    notification_dict = {"notification_id": notification_id, "action": "update", "updated_data": updated_data}
    notification_json = json.dumps(notification_dict).encode("utf-8")
    print("notification_JSON:", notification_json)
    
    await producer.send_and_wait("notification-event", notification_json)
    return updated_notification


@app.delete("/manage-notification/{notification_id}", response_model=dict)
async def delete_single_notification_route(
    notification_id: int,
    session: Annotated[Session, Depends(get_session)],
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
):
    """ Delete a single notification by ID and send a message to Kafka"""
    notification = get_notification_by_id(notification_id=notification_id, session=session)
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    delete_notification(notification_id=notification_id, session=session)

    notification_dict = {"notification_id": notification_id, "action": "delete"}
    notification_json = json.dumps(notification_dict).encode("utf-8")
    print("notification_JSON:", notification_json)

    await producer.send_and_wait("notification-event", notification_json)

    return {"message": "Notification deleted successfully", "notification_id": notification_id}

#Route For Validate Notification by ID

@app.get("/manage-notification/validate/{notification_id}", response_model=dict)
def validate_notification_route(
    notification_id: int,
    session: Annotated[Session, Depends(get_session)]
):
    """ Validate a single notification by ID"""
    is_valid = validate_notification(notification_id=notification_id, session=session)
    if is_valid:
        return {"message": "Notification is valid", "notification_id": notification_id}
    else:
        raise HTTPException(status_code=404, detail="Notification not found")