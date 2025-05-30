from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.product_model import Product, ProductUpdate

# Add a New Product to the Database
def add_new_product(product_data: Product, session: Session):
    """Add a new product to the database"""
    try:
        # Create a new Product instance
        new_product = Product(
            id=product_data.id,
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            expiry=product_data.expiry,
            brand=product_data.brand,
            weight=product_data.weight,
            category=product_data.category,
            sku=product_data.sku
        )
        print(f"Adding new product to DB: {new_product}")
        session.add(new_product)
        session.commit()
        session.refresh(new_product)
        return new_product
    except Exception as e:
        print(f"Error adding product to database: {str(e)}")
        session.rollback()
        raise

# Get All Products from the Database
def get_all_products(session: Session):
    all_products = session.exec(select(Product)).all()
    return all_products

# Get a Product by ID
def get_product_by_id(product_id: int, session: Session):
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Delete Product by ID
def delete_product_by_id(product_id: int, session: Session):
    # Step 1: Get the Product by ID
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    # Step 2: Delete the Product
    session.delete(product)
    session.commit()
    return {"message": "Product Deleted Successfully"}

# Update Product by ID
def update_product_by_id(product_id: int, to_update_product_data:ProductUpdate, session: Session):
    # Step 1: Get the Product by ID
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Step 2: Update the Product
    product_data = to_update_product_data.model_dump(exclude_unset=True)
    for key, value in product_data.items():
        setattr(product, key, value)
    
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

# Validate Product by ID
def validate_product_by_id(product_id: int, session: Session) -> Product | None:
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    return product