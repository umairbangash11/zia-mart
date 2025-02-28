from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from app.crud.notification_crud import validate_notification
from app.deps import get_session
#from app.hello_ai import chat_completion

async def consume_user_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="user-order-add-groups",
        # auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("\n\n RAW USER MESSAGE\n\n!!!!!")
            print(f"Received message on topic {message.topic}")
            print(f"Message Value {message.value}")

            # 1. Extract Poduct Id
            user_data = json.loads(message.value.decode())
            notification_id = user_data("notification_id")
            print("NOTIFICATION ID", notification_id)

            # 2. Check if Product Id is Valid
            with next(get_session()) as session:
                notification = validate_notification(
                    notification_id=notification_id, session=session)
                print("NOTIFICATION VALIDATION CHECK", notification)
                # 3. If Valid
                # if product is None:
                #     email_body = chat_completion(f"Admin has Sent InCorrect Product. Write Email to Admin {product_id}")
                    
                if notification is not None:
                        # - Write New Topic
                    print("NOTIFICATION VALIDATION CHECK NOT NONE")
                    
                    producer = AIOKafkaProducer(
                        bootstrap_servers='broker:19092')
                    await producer.start()
                    try:
                        await producer.send_and_wait(
                            "user-added-response",
                            message.value
                        )
                    finally:
                        await producer.stop()

            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()
