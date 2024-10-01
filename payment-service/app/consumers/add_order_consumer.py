from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from app.crud.transaction_crud import validate_transaction_by_id
from app.deps import get_session
#from app.hello_ai import chat_completion

async def consume_order_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="order-add-groups",
        # auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("\n\n RAW ORDER MESSAGE\n\n!!!!!")
            print(f"Received message on topic {message.topic}")
            print(f"Message Value {message.value}")

            # 1. Extract Poduct Id
            order_data = json.loads(message.value.decode())
            transaction_id = order_data("transaction_id")
            print("TRANSACTION ID", transaction_id)

            # 2. Check if Product Id is Valid
            with next(get_session()) as session:
                transaction = validate_transaction_by_id(
                    transaction_id=transaction_id, session=session)
                print("TRANSACTION VALIDATION CHECK", transaction)
                # 3. If Valid
                # if product is None:
                #     email_body = chat_completion(f"Admin has Sent InCorrect Product. Write Email to Admin {product_id}")
                    
                if transaction is not None:
                        # - Write New Topic
                    print("TRANSACTION VALIDATION CHECK NOT NONE")
                    
                    producer = AIOKafkaProducer(
                        bootstrap_servers='broker:19092')
                    await producer.start()
                    try:
                        await producer.send_and_wait(
                            "order-added-response",
                            message.value
                        )
                    finally:
                        await producer.stop()

            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()
