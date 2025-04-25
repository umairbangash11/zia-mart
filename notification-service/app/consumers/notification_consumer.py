from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from app.models.notification_model import Notification
from app.crud.notification_crud import create_notification
from app.deps import get_session
from sqlmodel import Session
from app.db_engine import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def consume_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="notification-consumer-group",
        auto_offset_reset="earliest",  # Start reading from the beginning
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            try:
                print(f"Received message on topic {message.topic}")
                notification_data = json.loads(message.value.decode())
                print(f"Notification Data: {notification_data}")

                # Create a new session for each message
                with Session(engine) as session:
                    try:
                        print("Attempting to save data to database")
                        notification = Notification(**notification_data)
                        db_insert_notification = create_notification(
                            notification=notification, 
                            session=session
                        )
                        print(f"Successfully saved notification: {db_insert_notification}")
                    except Exception as db_error:
                        print(f"Database error: {str(db_error)}")
                        # Don't raise the error, just log it and continue processing
                        continue
            except json.JSONDecodeError as json_error:
                print(f"JSON decode error: {str(json_error)}")
            except Exception as e:
                print(f"Error processing message: {str(e)}")
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()







