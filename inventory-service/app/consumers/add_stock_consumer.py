from aiokafka import AIOKafkaConsumer
import json
from sqlmodel import Session
from app.db_engine import engine
from app.crud.inventory_crud import add_new_inventory_item
from app.models.inventory_model import InventoryItem

async def consume_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="inventory-consumer-group",
        auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("RAW ADD STOCK CONSUMER MESSAGE!!")
            print(f"Received message on topic {message.topic}")

            try:
                inventory_data = json.loads(message.value.decode())
                print("TYPE", (type(inventory_data)))
                print(f"Inventory Data {inventory_data}")

                # Create a new session for each message
                with Session(engine) as session:
                    try:
                        print("SAVING DATA TO DATABASE")
                        # Create InventoryItem instance from the data
                        inventory_item = InventoryItem(**inventory_data)
                        # Add to database
                        db_insert_inventory = add_new_inventory_item(
                            inventory_item_data=inventory_item, 
                            session=session
                        )
                        print("DB_INSERT_STOCK", db_insert_inventory)
                    except Exception as db_error:
                        print(f"Database error: {str(db_error)}")
                        continue
            except json.JSONDecodeError as json_error:
                print(f"Error decoding JSON: {str(json_error)}")
                continue
            except Exception as e:
                print(f"Error processing message: {str(e)}")
                continue
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()

