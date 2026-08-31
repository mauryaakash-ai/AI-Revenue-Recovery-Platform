from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Merchant
from app.analytics import AnalyticsEngine

router = APIRouter()


@router.get("/merchants/{merchant_id}/analytics/overview")
async def get_overview(
    merchant_id: str,
    timeframe: str = "7D",
    db: Session = Depends(get_db)
):
    """Get Control Center Overview with KPIs, Funnel, Charts, Top Opps & AI Insights"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        # Fallback to primary merchant if not found
        merchant = db.query(Merchant).first()
        if not merchant:
            raise HTTPException(status_code=404, detail="Merchant not found")
        merchant_id = merchant.id
    
    return AnalyticsEngine.get_control_center_overview(db, merchant_id, timeframe)


@router.get("/merchants/{merchant_id}/analytics/payment-methods")
async def get_payment_methods_intelligence(
    merchant_id: str,
    db: Session = Depends(get_db)
):
    """Get payment method recovery vs failure intelligence"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first() or db.query(Merchant).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return AnalyticsEngine.get_payment_method_intelligence(db, merchant.id)


@router.get("/merchants/{merchant_id}/analytics/failures-breakdown")
async def get_failures_breakdown(
    merchant_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get failure breakdown by reason and bank with spike detection"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first() or db.query(Merchant).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return AnalyticsEngine.get_failure_analytics(db, merchant.id, days)


@router.get("/merchants/{merchant_id}/analytics/forecast")
async def get_forecast(
    merchant_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get 7-day revenue recovery forecast with confidence intervals"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first() or db.query(Merchant).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return AnalyticsEngine.get_revenue_forecast(db, merchant.id, days)


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
    
    return AnalyticsEngine.get_revenue(db, merchant_id, days)


@router.get("/merchants/{merchant_id}/analytics/success-rate")
async def get_success_rate(
    merchant_id: str,
    days: int = 7,
    payment_method: str = None,
    db: Session = Depends(get_db)
):
    """Get payment success rate"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    return AnalyticsEngine.get_payment_success_rate(db, merchant_id, days, payment_method)


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
    
    return AnalyticsEngine.get_failed_payments(db, merchant_id, days)


@router.get("/merchants/{merchant_id}/analytics/customers")
async def get_customers(
    merchant_id: str,
    db: Session = Depends(get_db)
):
    """Get customer statistics"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    return AnalyticsEngine.get_customers(db, merchant_id)


@router.get("/merchants/{merchant_id}/analytics/customer/{customer_id}")
async def get_customer_history(
    merchant_id: str,
    customer_id: str,
    days: int = 90,
    db: Session = Depends(get_db)
):
    """Get customer transaction history"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    return AnalyticsEngine.get_customer_history(db, merchant_id, customer_id, days)


@router.get("/merchants/{merchant_id}/analytics/refunds")
async def get_refunds(
    merchant_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get refund statistics"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    return AnalyticsEngine.get_refunds(db, merchant_id, days)


@router.get("/merchants/{merchant_id}/analytics/settlements")
async def get_settlements(
    merchant_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get settlement statistics"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    return AnalyticsEngine.get_settlements(db, merchant_id, days)


@router.get("/merchants/{merchant_id}/analytics/checkout-events")
async def get_checkout_events(
    merchant_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get checkout funnel analysis"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    return AnalyticsEngine.get_checkout_events(db, merchant_id, days)


@router.get("/merchants/{merchant_id}/analytics/anomalies")
async def detect_anomalies(
    merchant_id: str,
    baseline_days: int = 7,
    db: Session = Depends(get_db)
):
    """Detect revenue anomalies"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    return AnalyticsEngine.detect_anomalies(db, merchant_id, baseline_days)


@router.get("/merchants/{merchant_id}/analytics/revenue-loss")
async def get_revenue_loss(
    merchant_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Calculate confirmed revenue loss"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    return AnalyticsEngine.calculate_revenue_loss(db, merchant_id, days)


@router.get("/merchants/{merchant_id}/analytics/revenue-at-risk")
async def get_revenue_at_risk(
    merchant_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Calculate revenue at risk with confidence bounds"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    return AnalyticsEngine.calculate_revenue_at_risk(db, merchant_id, days)


@router.get("/merchants/{merchant_id}/analytics/recovery-predictions/{transaction_id}")
async def get_recovery_prediction(
    merchant_id: str,
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """Get recovery prediction for a specific transaction"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    return AnalyticsEngine.predict_recovery_probability(db, transaction_id)


@router.get("/merchants/{merchant_id}/analytics/segments")
async def get_segments(
    merchant_id: str,
    db: Session = Depends(get_db)
):
    """Get customer segmentation"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    return AnalyticsEngine.segment_customers(db, merchant_id)


@router.get("/merchants/{merchant_id}/analytics/top-leaks")
async def get_top_leaks(
    merchant_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get top revenue leaks ranked by recovery potential"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    return AnalyticsEngine.get_top_revenue_leaks(db, merchant_id, limit)

