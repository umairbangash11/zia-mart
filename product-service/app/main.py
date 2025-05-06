# main.py
from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json
import logging

from app import settings
from app.db_engine import engine
from app.models.product_model import Product, ProductUpdate
from app.crud.product_crud import (add_new_product,
                                    get_all_products, get_product_by_id, 
                                    delete_product_by_id, update_product_by_id,validate_product_by_id)
from app.deps import get_session, get_kafka_producer
from app.consumers.product_consumer import consume_messages
#from app.consumers.inventroy_consumer import consume_inventory_messages
#from app.consumers.pro_order_consumer import consume_product_order_messages
#from app.hello_ai import chat_completion
# from app.crud.rating_crud import (
#     add_new_rating,
#     get_rating_by_id,
#     delete_rating_by_id,
#     get_all_ratings_for_product,
#     update_rating_by_id
# )
# from app.consumers.product_rating_consumer import consume_rating_messages
# from app.hello_ai import chat_completion

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

# Store the consumer task globally
consumer_task = None

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global consumer_task
    
    try:
        # First create the database tables
        logger.info("Creating database tables...")
        create_db_and_tables()
        
        # Then start the consumer
        logger.info("Starting Kafka consumer...")
        consumer_task = asyncio.create_task(consume_messages(
            settings.KAFKA_PRODUCT_TOPIC, 
            settings.BOOTSTRAP_SERVER
        ))
        
        # Add error handling for the consumer task
        def handle_consumer_error(task):
            try:
                task.result()
            except Exception as e:
                logger.error(f"Consumer task failed: {str(e)}")
                # Restart the consumer
                global consumer_task
                consumer_task = asyncio.create_task(consume_messages(
                    settings.KAFKA_PRODUCT_TOPIC, 
                    settings.BOOTSTRAP_SERVER
                ))
                consumer_task.add_done_callback(handle_consumer_error)
        
        consumer_task.add_done_callback(handle_consumer_error)
        
        yield
        
    except Exception as e:
        logger.error(f"Error in lifespan: {str(e)}")
        raise
    finally:
        # Clean up the consumer task
        if consumer_task:
            consumer_task.cancel()
            try:
                await consumer_task
            except asyncio.CancelledError:
                pass


app = FastAPI(
    lifespan=lifespan,
    title="Product Service API",
    version="0.0.1",
)



@app.get("/")
def read_root():
    return {"Hello": "Product Service"}


@app.post("/manage-products/", response_model=Product)
async def create_new_product(product: Product, 
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    """Create a new product and send it to Kafka"""
    try:
        # Convert product to dict and add action
        product_dict = product.model_dump()
        product_dict["action"] = "create"
        
        # Send to Kafka
        await producer.send_and_wait(
            settings.KAFKA_PRODUCT_TOPIC, 
            json.dumps(product_dict).encode()
        )
        return product
    except Exception as e:
        logger.error(f"Error sending message to Kafka: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send message to Kafka: {str(e)}")


@app.get("/manage-products/all", response_model=list[Product])
def call_all_products(session: Annotated[Session, Depends(get_session)]):
    """Get all products from the database"""
    return get_all_products(session)


@app.get("/manage-products/{product_id}", response_model=Product)
def get_single_product(product_id: int, session: Annotated[Session, Depends(get_session)]):
    """Get a single product by ID"""

    try:
        return get_product_by_id(product_id=product_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/manage-products/{product_id}", response_model=Product)
async def delete_single_product(
    product_id: int,
    session: Annotated[Session, Depends(get_session)],
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
):
    """Delete a single product by ID and send a message to Kafka"""

    try:
        # Delete the product from the database
        deleted_product = delete_product_by_id(product_id=product_id, session=session)
        if not deleted_product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Send delete message to Kafka
        delete_message = {
            "id": product_id,
            "action": "delete"
        }
        await producer.send_and_wait(
            settings.KAFKA_PRODUCT_TOPIC, 
            json.dumps(delete_message).encode()
        )
        
        return {"message": "Product deleted successfully", "product_id": product_id}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/manage-products/{product_id}", response_model=Product)
async def update_single_product(
    product_id: int,
    product: ProductUpdate,
    session: Annotated[Session, Depends(get_session)],
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
):
    """Update a single product by ID and send a message to Kafka"""
    try:
        # Update the product in the database
        updated_product = update_product_by_id(
            product_id=product_id, 
            to_update_product_data=product, 
            session=session
        )
        if not updated_product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Convert to dict and add action
        update_dict = product.model_dump(exclude_unset=True)
        update_dict["id"] = product_id
        update_dict["action"] = "update"
        
        # Send to Kafka
        await producer.send_and_wait(
            settings.KAFKA_PRODUCT_TOPIC, 
            json.dumps(update_dict).encode()
        )
        
        return updated_product

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/validate-product/{product_id}", response_model=Product)
async def validate_product(product_id: int, session: Session = Depends(get_session)):
    product = validate_product_by_id(product_id, session)
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


# @app.get("/hello-ai")
# def get_ai_response(prompt:str):
#     return chat_completion(prompt)