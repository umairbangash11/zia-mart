from aiokafka import AIOKafkaConsumer
import json
from app.models.product_model import Product
from app.crud.product_crud import add_new_product, update_product_by_id, delete_product_by_id
from app.db_engine import engine
from sqlmodel import Session
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def consume_messages(topic: str, bootstrap_servers: str):
    logger.info(f"Starting consumer for topic: {topic}")
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="product-consumer-group",
        auto_offset_reset="earliest"
    )

    try:
        await consumer.start()
        logger.info("Consumer started successfully")
        
        async for message in consumer:
            logger.info(f"Received message on topic {message.topic}")
            
            try:
                # Parse the JSON message
                message_data = json.loads(message.value.decode())
                logger.info(f"Received message data: {message_data}")
                
                # Handle different message types based on action
                action = message_data.get("action", "create")
                
                if action == "create":
                    # Create new product
                    product = Product(**message_data)
                    with Session(engine) as session:
                        added_product = add_new_product(product_data=product, session=session)
                        logger.info(f"Successfully added product to database: {added_product.name}")
                
                elif action == "update":
                    # Update existing product
                    product_id = message_data.pop("id")
                    product_update = Product(**message_data)
                    with Session(engine) as session:
                        updated_product = update_product_by_id(
                            product_id=product_id,
                            to_update_product_data=product_update,
                            session=session
                        )
                        logger.info(f"Successfully updated product in database: {updated_product.name}")
                
                elif action == "delete":
                    # Delete product
                    product_id = message_data.get("id")
                    with Session(engine) as session:
                        delete_product_by_id(product_id=product_id, session=session)
                        logger.info(f"Successfully deleted product from database: {product_id}")
                
                else:
                    logger.warning(f"Unknown action type: {action}")
                    
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Consumer error: {str(e)}")
        raise
    finally:
        logger.info("Stopping consumer")
        await consumer.stop()



