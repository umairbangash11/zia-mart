from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from app.models.product_model import Product, ProductUpdate
from app.crud.product_crud import add_new_product, get_all_products, get_product_by_id, delete_product_by_id, update_product_by_id
from app.deps import get_session
from app import settings
from sqlmodel import Session
from app.db_engine import engine


async def consume_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=settings.KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT,
        auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print(f"Received message on topic {message.topic}")
            print(f"Message value: {message.value}")

            try:
                product_data = json.loads(message.value.decode())
                print(f"Product Data: {product_data}")

                # Create a new session for each message
                with Session(engine) as session:
                    print("Saving data to database")
                    if isinstance(product_data, dict):
                        try:
                            # Create Product instance from the data
                            product = Product(**product_data)
                            # Add to database
                            db_insert_product = add_new_product(
                                product_data=product, session=session)
                            print(f"Product saved to database: {db_insert_product}")
                        except Exception as e:
                            print(f"Error creating or saving product: {str(e)}")
                            continue
                    else:
                        print(f"Invalid message format: {product_data}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {str(e)}")
                continue
            except Exception as e:
                print(f"Error processing message: {str(e)}")
                continue
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()



