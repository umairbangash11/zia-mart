from sqlmodel import SQLModel, Field, Relationship

class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str
    price: float
    expiry: str | None = None
    brand: str | None = None
    weight: float | None = None
    category: str # It shall be pre defined by Platform
    sku: str | None = None
    #rating: list["ProductRating"] = Relationship(back_populates="product")
    # image: str # Multiple | URL Not Media | One to Manu Relationship
    # quantity: int | None = None # Shall it be managed by Inventory Microservice
    # color: str | None = None # One to Manu Relationship
    # rating: float | None = None # One to Manu Relationship


class ProductUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    expiry: str | None = None
    brand: str | None = None
    weight: float | None = None
    category: str | None = None
    sku: str | None = None

