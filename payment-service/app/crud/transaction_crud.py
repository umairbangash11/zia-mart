from sqlmodel import Session, select
from app.models.transaction_model import Transaction, TransactionUpdate, TransactionDelete
from fastapi import HTTPException

def create_transaction(transaction_data: Transaction, session: Session):
    print("Adding Transaction to Database")
    session.add(transaction_data)
    session.commit()
    session.refresh(transaction_data)
    return transaction_data

def get_all_transactions(session: Session):
    all_transaction= session.exec(select(Transaction)).all()
    return all_transaction

def get_transaction_by_id(session: Session, transaction_id: int):
    transaction = session.exec(select(Transaction).where(Transaction.id == transaction_id)).one_or_none()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

def update_transaction(
    session: Session, 
    transaction_id: int, 
    transaction_update: TransactionUpdate ):
    # Fetch the existing transaction
    transaction = session.exec(select(Transaction).where(Transaction.id == transaction_id)).one_or_none()
    
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Update fields that are provided in transaction_update
    update_data = transaction_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(transaction, key, value)
    
    # Commit changes to the database
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    
    return transaction


def delete_transaction(session: Session, transaction_id: int):
    # Fetch the existing transaction
    transaction = session.exec(select(Transaction).where(Transaction.id == transaction_id)).one_or_none()
    
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Delete the transaction from the database
    session.delete(transaction)
    session.commit()
    
    return {"detail": "Transaction deleted successfully"}


#Validate Transaction By Id
def validate_transaction_by_id(transaction_id: int, session: Session) -> Transaction | None:
    transaction = session.exec(select(Transaction).where(Transaction.id == transaction_id)).one_or_none()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

