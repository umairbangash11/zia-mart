# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from app import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select, Sequence
from fastapi import FastAPI, Depends
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json
from app import todo_pb2


class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(index=True)


# Get the database URL from settings and ensure it's properly formatted
database_url = str(settings.DATABASE_URL)
if database_url.startswith('DATABASE_URL='):
    database_url = database_url.replace('DATABASE_URL=', '')

# Replace postgresql with postgresql+psycopg for psycopg 3
connection_string = database_url.replace("postgresql", "postgresql+psycopg")

# Create engine with connection pooling
engine = create_engine(
    connection_string,
    connect_args={},
    pool_recycle=300  # recycle connections after 5 minutes
)

# engine = create_engine(
#    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
# )


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


async def consume_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="my-group",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print(f"Received message: {
                  message.value.decode()} on topic {message.topic}")

            new_todo = todo_pb2.Todo()
            new_todo.ParseFromString(message.value)
            print(f"\n\n Consumer Deserialized data: {new_todo}")

            # # Add todo to DB
            with next(get_session()) as session:
                todo = Todo(id=new_todo.id, content=new_todo.content)
                session.add(todo)
                session.commit()
                session.refresh(todo)

            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()


# The first part of the function, before the yield, will
# be executed before the application starts.
# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
# loop = asyncio.get_event_loop()
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables.")
    # loop.run_until_complete(consume_messages('todos', 'broker:19092'))
    task = asyncio.create_task(consume_messages('todos2', 'broker:19092'))
    create_db_and_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Hello World API with DB",
    version="0.0.1",
)


def get_session():
    with Session(engine) as session:
        yield session


@app.get("/")
def read_root():
    return {"Hello": "PanaCloud"}

# Kafka Producer as a dependency


async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()


@app.post("/todos/", response_model=Todo)
async def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]) -> Todo:
    todo_protbuf = todo_pb2.Todo(id=todo.id, content=todo.content)
    print(f"Todo Protobuf: {todo_protbuf}")
    serialized_todo = todo_protbuf.SerializeToString()
    print(f"Serialized data: {serialized_todo}")
    await producer.send_and_wait("todos2", serialized_todo)

    # Save to database
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@app.get("/todos/", response_model=list[Todo])
def read_todos(session: Annotated[Session, Depends(get_session)]):
    todos = session.exec(select(Todo)).all()
    return todos
