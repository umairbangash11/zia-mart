from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from app.models.order_model import Order
from app.crud.order_crud import track_order_by_id
from app.deps import get_session, get_kafka_producer
from app.hello_ai import chat_completion

async def consume_notification_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="notification-add-groups",
        # auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("\n\n RAW NOTIFICATION MESSAGE\n\n ")
            print(f"Received message on topic {message.topic}")
            print(f"Message Value {message.value}")

            # 1. Extract Poduct Id
            notification_data = json.loads(message.value.decode())
            order_id = notification_data["order_id"]
            print("ORDER ID", order_id)

            # 2. Check if Product Id is Valid
            with next(get_session()) as session:
                order = track_order_by_id(
                    order_id=order_id, session=session)
                print("ORDER TRACK CHECK", order)
                # 3. If Valid
                if order is None:
                    email_body = chat_completion(f"Admin has Sent InCorrect Order. Write Email to Admin {order_id}")
                    
                if order is not None:
                        # - Write New Topic
                    print("ORDER TRACK CHECK NOT NONE")
                    
                    producer = AIOKafkaProducer(
                        bootstrap_servers='broker:19092')
                    await producer.start()
                    try:
                        await producer.send_and_wait(
                            "order-response",
                            message.value
                        )
                    finally:
                        await producer.stop()

            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()
