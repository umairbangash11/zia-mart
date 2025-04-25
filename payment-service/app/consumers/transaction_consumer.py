from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from app.models.transaction_model import Transaction
from app.crud.transaction_crud import create_transaction
from app.deps import get_session
from sqlmodel import Session
from app.db_engine import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def consume_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="transaction-consumer-group",
        auto_offset_reset="earliest",  # Start reading from the beginning
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            try:
                print(f"Received message on topic {message.topic}")
                transaction_data = json.loads(message.value.decode())
                print(f"Transaction Data: {transaction_data}")

                # Validate required fields
                required_fields = ['user_id', 'order_id', 'amount', 'status']
                missing_fields = [field for field in required_fields if field not in transaction_data]
                if missing_fields:
                    print(f"Missing required fields: {missing_fields}")
                    continue

                # Create a new session for each message
                with Session(engine) as session:
                    try:
                        print("Attempting to save data to database")
                        transaction = Transaction(**transaction_data)
                        db_insert_transaction = create_transaction(
                            transaction_data=transaction, 
                            session=session
                        )
                        print(f"Successfully saved transaction: {db_insert_transaction}")
                    except Exception as db_error:
                        print(f"Database error: {str(db_error)}")
                        # Don't raise the error, just log it and continue processing
                        continue
            except json.JSONDecodeError as json_error:
                print(f"JSON decode error: {str(json_error)}")
            except Exception as e:
                print(f"Error processing message: {str(e)}")
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()



