# main.py
from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json

from app import settings
from app.db_engine import engine
from app.models.transaction_model import Transaction, TransactionUpdate, TransactionDelete
from app.crud.transaction_crud import (
get_transaction_by_id,
update_transaction, 
delete_transaction,
get_all_transactions,
validate_transaction_by_id)
from app.deps import get_session, get_kafka_producer
from app.consumers.transaction_consumer import consume_messages
# app.consumers.send_not_consumer import consume_notification_messages
#from app.consumers.add_order_consumer import consume_order_messages


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

# The first part of the function, before the yield, will
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating ... ... ?? !!!! ")

    task = asyncio.create_task(consume_messages(
        "transaction-event", 'broker:19092'))
    
    # asyncio.create_task(consume_notification_messages(
    #     "notification-event",
    #     #settings.KAFKA_INVENTORY_TOPIC,
    #     'broker:19092'
        
    # ))

    # asyncio.create_task(consume_notification_messages(
    #     "order-events",
    #     #settings.KAFKA_INVENTORY_TOPIC,
    #     'broker:19092'
        
    # ))

    create_db_and_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Hello World API with DB",
    version="0.0.1",
)


@app.get("/")
def read_root():
    return {"Hello": "Payment Service"}


@app.post("/transactions/", response_model=Transaction)
async def create_payment_transaction(
    transaction: Transaction,
    session: Annotated[Session, Depends(get_session)], 
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
):
    """Create a new transaction and send it to Kafka"""

    # Convert the Transaction object to a dictionary
    transaction_dict = {field: getattr(transaction, field) for field in transaction.dict()}
    transaction_json = json.dumps(transaction_dict).encode("utf-8")

    # Produce Kafka message
    await producer.send_and_wait("transaction-event", transaction_json)

    return transaction

@app.get("/manage_transactions/all", response_model=list[Transaction])
def get_all_transactions_route(session: Annotated[Session, Depends(get_session)]):
    
    return get_all_transactions(session)

@app.get("/manage_transactions/{transaction_id}", response_model=Transaction)
def read_transaction(transaction_id: int, session: Session = Depends(get_session)):
    try:
        return get_transaction_by_id(transaction_id=transaction_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/transactions/{transaction_id}", response_model=dict)
async def delete_transaction_route(
    transaction_id: int,
    session: Annotated[Session, Depends(get_session)],
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
):
    """ Delete a transaction by ID and send a message to Kafka"""

    try:
        # Delete the transaction from the database
        success = delete_transaction(session, transaction_id)
        if not success:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # Prepare the Kafka message
        transaction_dict = {"transaction_id": transaction_id, "action": "delete"}
        transaction_json = json.dumps(transaction_dict).encode("utf-8")
        print("transaction_JSON:", transaction_json)

        # Produce message to Kafka
        await producer.send_and_wait("transaction-event", transaction_json)

        # Return a success response
        return {"message": "Transaction deleted successfully", "transaction_id": transaction_id}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
   
@app.patch("/manage-transactions/{transaction_id}", response_model=Transaction)
async def update_single_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    session: Annotated[Session, Depends(get_session)],
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
):
    """ Update a single transaction by ID and send a message to Kafka"""
    try:
        # Update the transaction in the database
        updated_transaction = update_transaction(
            session=session,
            transaction_id=transaction_id,
            transaction_update=transaction_update  # Correct way
        )
 
        if updated_transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # Prepare the Kafka message
        updated_data = updated_transaction.dict()

        # Convert created_at to a string, if it exists
        if "created_at" in updated_data and updated_data["created_at"] is not None:
            updated_data["created_at"] = updated_data["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        transaction_dict = {
            "transaction_id": transaction_id,
            "action": "update",
            "updated_data": updated_data
        }

        transaction_json = json.dumps(transaction_dict).encode("utf-8")
        print("transaction_JSON:", transaction_json)

        # Produce message to Kafka
        await producer.send_and_wait("transaction-event", transaction_json)

        # Return the updated transaction
        return updated_transaction

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#Create Validate Transaction By Id
@app.get("/validate_transaction/{transaction_id}", response_model=Transaction)
def validate_transaction(transaction_id: int, session: Session = Depends(get_session)):
    try:
        # Correct order of arguments
        return validate_transaction_by_id(transaction_id, session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
