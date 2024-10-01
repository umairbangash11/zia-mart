from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from app.models.inventory_model import InventoryItem
from app.crud.inventory_crud import validate_inventory_item_id
from app.deps import get_session
#from app.hello_ai import chat_completion

async def consume_invent_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="order-consumer-group",
        # auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("\n\n RAW INVENTORY MESSAGE\n\n ")
            print(f"Received message on topic {message.topic}")
            print(f"Message Value {message.value}")

            # 1. Extract Poduct Id
            order_data = json.loads(message.value.decode())
            inventory_item_id = order_data["inventory_item_id"]
            print("INVENTORY ID", inventory_item_id)

            # 2. Check if Product Id is Valid
            with next(get_session()) as session:
                inventory = validate_inventory_item_id(
                    inventory_item_id=inventory_item_id, session=session)
                print("INVENTORY TRACK CHECK", inventory)
                # 3. If Valid
                # if order is None:
                #     email_body = chat_completion(f"Admin has Sent InCorrect Order. Write Email to Admin {order_id}")
                    
                if inventory is not None:
                        # - Write New Topic
                    print("INVENTORY TRACK CHECK NOT NONE")
                    
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
