from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Transaction, Merchant, TransactionStatus
from datetime import datetime, timedelta
from sqlalchemy import func

router = APIRouter()


@router.get("/merchants/{merchant_id}/analytics/revenue")
async def get_revenue(
    merchant_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get revenue analytics"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Calculate total revenue
    total_revenue = db.query(func.sum(Transaction.amount)).filter(
        Transaction.merchant_id == merchant_id,
        Transaction.status == TransactionStatus.SUCCESS,
        Transaction.created_at >= cutoff_date
    ).scalar() or 0.0
    
    # Calculate today's revenue
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_revenue = db.query(func.sum(Transaction.amount)).filter(
        Transaction.merchant_id == merchant_id,
        Transaction.status == TransactionStatus.SUCCESS,
        Transaction.created_at >= today_start
    ).scalar() or 0.0
    
    # Calculate yesterday's revenue
    yesterday_start = (datetime.utcnow() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = yesterday_start + timedelta(days=1)
    yesterday_revenue = db.query(func.sum(Transaction.amount)).filter(
        Transaction.merchant_id == merchant_id,
        Transaction.status == TransactionStatus.SUCCESS,
        Transaction.created_at >= yesterday_start,
        Transaction.created_at < yesterday_end
    ).scalar() or 0.0
    
    delta = today_revenue - yesterday_revenue
    delta_pct = (delta / yesterday_revenue * 100) if yesterday_revenue > 0 else 0
    
    return {
        "total_revenue": total_revenue,
        "today_revenue": today_revenue,
        "yesterday_revenue": yesterday_revenue,
        "delta": delta,
        "delta_percentage": delta_pct
    }


@router.get("/merchants/{merchant_id}/analytics/success-rate")
async def get_success_rate(
    merchant_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get payment success rate"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    total = db.query(func.count(Transaction.id)).filter(
        Transaction.merchant_id == merchant_id,
        Transaction.created_at >= cutoff_date
    ).scalar() or 0
    
    successful = db.query(func.count(Transaction.id)).filter(
        Transaction.merchant_id == merchant_id,
        Transaction.status == TransactionStatus.SUCCESS,
        Transaction.created_at >= cutoff_date
    ).scalar() or 0
    
    success_rate = (successful / total * 100) if total > 0 else 0
    
    return {
        "success_rate": success_rate,
        "successful_transactions": successful,
        "total_transactions": total
    }


@router.get("/merchants/{merchant_id}/analytics/failed-payments")
async def get_failed_payments(
    merchant_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get failed payments and their reasons"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    failed = db.query(Transaction).filter(
        Transaction.merchant_id == merchant_id,
        Transaction.status == TransactionStatus.FAILED,
        Transaction.created_at >= cutoff_date
    ).all()
    
    # Group by failure reason
    reasons = {}
    for t in failed:
        reason = t.failure_reason or "unknown"
        if reason not in reasons:
            reasons[reason] = {"count": 0, "amount": 0}
        reasons[reason]["count"] += 1
        reasons[reason]["amount"] += t.amount
    
    return {
        "total_failed": len(failed),
        "failed_amount": sum(f.amount for f in failed),
        "by_reason": reasons
    }
