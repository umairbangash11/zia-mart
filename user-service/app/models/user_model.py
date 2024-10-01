from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    

    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    hashed_password: str
    is_active: bool = Field(default=True)

class UserRead(SQLModel):
    id: int
    username: str
    email: str
    is_active: bool

class UserCreate(SQLModel):
    username: str
    email: str
    password: str

class UserResponseWithToken(SQLModel):
    id: int
    username: str
    email: str
    is_active: bool
    access_token: str
    token_type: str

