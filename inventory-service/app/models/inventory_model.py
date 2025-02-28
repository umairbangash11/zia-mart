from sqlmodel import SQLModel, Field, Relationship

# Inventory Microservice Models
class InventoryItemBase(SQLModel):
    product_id: int
    variant_id: int | None = None
    quantity: int
    status: str 

class InventoryItem(InventoryItemBase, table=True):
    id: int = Field(default=None, primary_key=True)


class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItemRead(InventoryItemBase):
    id: int

# InventoryItemUpdate
class InventoryItemUpdate(SQLModel):
    quantity: int | None = None
    status: str | None = None
    product_id: int | None = None
    variant_id: int | None = None




