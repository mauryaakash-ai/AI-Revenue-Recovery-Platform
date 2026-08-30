from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Transaction, Merchant
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/merchants/{merchant_id}/transactions")
async def get_transactions(
    merchant_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get transactions for a merchant"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    transactions = db.query(Transaction).filter(
        Transaction.merchant_id == merchant_id,
        Transaction.created_at >= cutoff_date
    ).order_by(Transaction.created_at.desc()).all()
    
    return {
        "merchant_id": merchant_id,
        "count": len(transactions),
        "transactions": [
            {
                "id": t.id,
                "amount": t.amount,
                "currency": t.currency,
                "payment_method": t.payment_method,
                "status": t.status,
                "created_at": t.created_at
            }
            for t in transactions
        ]
    }


@router.get("/merchants/{merchant_id}/transactions/{transaction_id}")
async def get_transaction(
    merchant_id: str,
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific transaction"""
    transaction = db.query(Transaction).filter(
        Transaction.merchant_id == merchant_id,
        Transaction.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return {
        "id": transaction.id,
        "amount": transaction.amount,
        "currency": transaction.currency,
        "payment_method": transaction.payment_method,
        "status": transaction.status,
        "failure_reason": transaction.failure_reason,
        "product_id": transaction.product_id,
        "order_id": transaction.order_id,
        "device_type": transaction.device_type,
        "location": transaction.location,
        "created_at": transaction.created_at
    }
