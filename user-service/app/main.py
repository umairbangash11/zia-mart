from fastapi import FastAPI, Depends, HTTPException
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.auth.user_auth import create_access_token, decode_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from app.crud.user_crud import get_user_by_username, create_user, get_all_users, get_user_by_id
from app.models.user_model import UserCreate, UserRead, UserResponseWithToken
from app.deps import get_session, get_kafka_producer
from sqlmodel import Session, SQLModel
from app.db_engine import engine
from aiokafka import AIOKafkaProducer
import json
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncio
from app import settings
from app.consumers.user_consumer import consume_messages
#from app.consumers.send_not_consumer import consume_user_notification_messages
# from app.consumers.payment_consumer import consume_user_payment_messages
#from app.consumers.add_order_consumer import consume_user_order_messages

from typing import Annotated, List
from fastapi.security import OAuth2PasswordBearer


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

# Create database tables
def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating ... ... ?? !!!! ")

    task = asyncio.create_task(consume_messages(
        "order-events", 'broker:19092'))
    

    # asyncio.create_task(consume_user_notification_messages(
    #     "notification-event",
    #     #settings.KAFKA_INVENTORY_TOPIC,
    #     'broker:19092'
        
    # ))

    # asyncio.create_task(consume_user_payment_messages(
    #     "transaction-event",
    #     #settings.KAFKA_INVENTORY_TOPIC,
    #     'broker:19092'
        
    # ))

    # asyncio.create_task(consume_user_order_messages(
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
    return {"Hello": "User Service"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/signup", response_model=UserRead)
async def signup(
    user_create: UserCreate,  
    session: Annotated[Session, Depends(get_session)], 
    producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
):
    existing_user = get_user_by_username(user_create.username, session)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = create_user(user_create=user_create, session=session)
    user_dict = {field: getattr(user, field) for field in user.dict()}
    user_json = json.dumps(user_dict).encode("utf-8")
    print("user_JSON:", user_json)
    await producer.send_and_wait("user_events", user_json)
    return user

@app.post("/token", response_model=UserResponseWithToken)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: Session = Depends(get_session), 
    producer: AIOKafkaProducer = Depends(get_kafka_producer)
):
    user = get_user_by_username(form_data.username, session)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    login_event = {
        "username": user.username,
        "event": "login",
        "status": "successful",
        "access_token": access_token
    }
    login_json = json.dumps(login_event).encode("utf-8")
    print("login_JSON:", login_json)
    await producer.send_and_wait("user_events", login_json)
    return UserResponseWithToken(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        access_token=access_token,
        token_type="bearer"
    )


@app.get("/users/me", response_model=UserRead)
async def read_users_me(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        username = decode_access_token(token)
    except HTTPException as e:
        if "expired" in str(e.detail):
            raise HTTPException(status_code=401, detail="Token has expired. Please renew it.")
        raise e
    user = get_user_by_username(username, session)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/all", response_model=List[UserRead])
async def read_all_users(session: Session = Depends(get_session)):
    users = get_all_users(session)
    return users

@app.post("/renew-token")
async def renew_token(token: str = Depends(oauth2_scheme)):
    try:
        username = decode_access_token(token)
        new_token = create_access_token(data={"sub": username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return {"access_token": new_token, "token_type": "bearer"}
    except HTTPException as e:
        raise HTTPException(status_code=401, detail=str(e.detail))

@app.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int, session: Session = Depends(get_session)):
    # Call the get_user_by_id function
    user = get_user_by_id(user_id, session)
    if not user:
        # Raise 404 error if user is not found
        raise HTTPException(status_code=404, detail="User not found")
    return user