from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from app.models.inventory_model import InventoryItem
from sqlmodel import Session, select
from fastapi import HTTPException

from app.deps import get_session, get_kafka_producer
#from app.hello_ai import chat_completion

def validate_inventory_item_id(inventory_item_id: int, session: Session):
    inventory_item = session.exec(select(InventoryItem).where(InventoryItem.id == inventory_item_id)).one_or_none()
    if inventory_item is None:
        raise HTTPException(status_code=404, detail="Inventory Item not found")
    return inventory_item



async def consume_product_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="product-add-group",
        # auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("\n\n RAW PRODUCT MESSAGE\n\n ")
            print(f"Received message on topic {message.topic}")
            print(f"Message Value {message.value}")

            # 1. Extract Poduct Id
            product_data = json.loads(message.value.decode())
            inventory_id = product_data["inventory_id"]
            print("INVENTORY ID", inventory_id)

            # 2. Check if Product Id is Valid
            with next(get_session()) as session:
                inventory = validate_inventory_item_id(
                    inventory_id=inventory_id, session=session)
                print("PRODUCT VALIDATION CHECK", inventory)
                # 3. If Valid
                # if inventory is None:
                #     email_body = chat_completion(f"Admin has Sent InCorrect Product. Write Email to Admin {inventory_id}")
                    
                if inventory is not None:
                        # - Write New Topic
                    print("INVENTORY VALIDATION CHECK NOT NONE")
                    
                    producer = AIOKafkaProducer(
                        bootstrap_servers='broker:19092')
                    await producer.start()
                    try:
                        await producer.send_and_wait(
                            "product-add-stock-response",
                            message.value
                        )
                    finally:
                        await producer.stop()

            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()