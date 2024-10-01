from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from app.models.notification_model import Notification
from app.crud.notification_crud import create_notification
from app.deps import get_session


async def consume_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="notification-consumer-group",
        # auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("RAW")
            print(f"Received message on topic {message.topic}")

            notification_data = json.loads(message.value.decode())
            print("TYPE", (type(notification_data)))
            print(f"NOTIFICATION Data {notification_data}")

            with next(get_session()) as session:
                print("SAVING DATA TO DATABSE")
                db_insert_notification = create_notification(
                    notification=Notification(**notification_data), session=session)
                print("DB_INSERT_NOTIFICATION", db_insert_notification)
                   
                # Event EMIT In NEW TOPIC
            
            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()







