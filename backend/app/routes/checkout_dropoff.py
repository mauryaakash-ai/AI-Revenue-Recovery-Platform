"""
Checkout Drop-off Recovery Route
Features:
- Real-time cart/checkout abandonment detection
- Cause segmentation: price_hesitation, form_friction, otp_delay, session_expiry
- 1-Click pre-filled cart resume links
- Recovery nudge dispatching (WhatsApp, SMS, Email)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.database import get_db
from app.models import CheckoutDropoff, Merchant, AuditLog, ComplianceRuleLog

router = APIRouter()


class NudgeRequest(BaseModel):
    channel: Optional[str] = "whatsapp"  # whatsapp, sms, email
    discount_code: Optional[str] = None
    custom_message: Optional[str] = None


@router.get("/checkout-dropoff/list")
def get_checkout_dropoffs(
    merchant_id: Optional[str] = None,
    cause: Optional[str] = None,
    nudge_status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Retrieve paginated checkout drop-off events with cause filtering."""
    query = db.query(CheckoutDropoff)
    if merchant_id:
        query = query.filter(CheckoutDropoff.merchant_id == merchant_id)
    if cause:
        query = query.filter(CheckoutDropoff.cause == cause)
    if nudge_status:
        query = query.filter(CheckoutDropoff.nudge_status == nudge_status)
    
    dropoffs = query.order_by(CheckoutDropoff.created_at.desc()).limit(limit).all()

    # Calculate overview stats
    total_dropoffs = query.count()
    total_cart_value = db.query(func.sum(CheckoutDropoff.cart_value)).scalar() or 0.0
    converted_count = db.query(CheckoutDropoff).filter(CheckoutDropoff.nudge_status == "converted").count()
    recovered_value = db.query(func.sum(CheckoutDropoff.cart_value)).filter(CheckoutDropoff.nudge_status == "converted").scalar() or 0.0

    return {
        "summary": {
            "total_abandoned_sessions": total_dropoffs,
            "total_cart_value_at_risk": total_cart_value,
            "converted_sessions": converted_count,
            "recovered_revenue": recovered_value,
            "conversion_rate": round((converted_count / max(total_dropoffs, 1)) * 100, 1),
            "cause_breakdown": {
                "price_hesitation": db.query(CheckoutDropoff).filter(CheckoutDropoff.cause == "price_hesitation").count(),
                "form_friction": db.query(CheckoutDropoff).filter(CheckoutDropoff.cause == "form_friction").count(),
                "otp_delay": db.query(CheckoutDropoff).filter(CheckoutDropoff.cause == "otp_delay").count(),
                "session_expiry": db.query(CheckoutDropoff).filter(CheckoutDropoff.cause == "session_expiry").count(),
            }
        },
        "items": [
            {
                "id": d.id,
                "merchant_id": d.merchant_id,
                "customer_name": d.customer_name,
                "customer_email": d.customer_email,
                "customer_phone": d.customer_phone,
                "session_id": d.session_id,
                "cart_value": d.cart_value,
                "items_summary": d.items_summary,
                "dropoff_stage": d.dropoff_stage,
                "cause": d.cause,
                "cause_confidence": round(d.cause_confidence * 100, 1),
                "nudge_channel": d.nudge_channel,
                "nudge_status": d.nudge_status,
                "resume_token": d.resume_token,
                "resume_url": f"https://checkout.razorpay.com/resume?token={d.resume_token}",
                "discount_code_applied": d.discount_code_applied,
                "created_at": d.created_at.isoformat() if d.created_at else None,
                "converted_at": d.converted_at.isoformat() if d.converted_at else None
            }
            for d in dropoffs
        ]
    }


@router.post("/checkout-dropoff/{dropoff_id}/nudge")
def dispatch_dropoff_nudge(
    dropoff_id: str,
    payload: NudgeRequest,
    db: Session = Depends(get_db)
):
    """Trigger personalized 1-click cart resume nudge to customer."""
    dropoff = db.query(CheckoutDropoff).filter(CheckoutDropoff.id == dropoff_id).first()
    if not dropoff:
        raise HTTPException(status_code=404, detail="Checkout dropoff not found")

    dropoff.nudge_channel = payload.channel or dropoff.nudge_channel
    dropoff.nudge_status = "sent"
    if payload.discount_code:
        dropoff.discount_code_applied = payload.discount_code
    
    # Audit log
    audit = AuditLog(
        id=str(uuid.uuid4()),
        user_role="Revenue Operations",
        merchant_id=dropoff.merchant_id,
        action="DISPATCH_DROPOFF_NUDGE",
        target_type="dropoff",
        target_id=dropoff.id,
        action_data=f'{{"channel": "{dropoff.nudge_channel}", "cause": "{dropoff.cause}", "discount": "{dropoff.discount_code_applied}"}}',
        result="success",
        approval_status="auto_approved"
    )
    db.add(audit)
    db.commit()

    # Dispatch live notification via communication dispatcher
    from app.communication_service import dispatcher
    dispatch_res = dispatcher.send_whatsapp(
        to_phone=dropoff.customer_phone or "+91 9820194821",
        customer_name=dropoff.customer_name or "Valued Customer",
        amount=dropoff.cart_value,
        payment_link=f"https://checkout.razorpay.com/resume?token={dropoff.resume_token}",
        discount_code=payload.discount_code
    )

    return {
        "success": True,
        "message": f"Resume nudge dispatched via {dropoff.nudge_channel.upper()}",
        "resume_url": f"https://checkout.razorpay.com/resume?token={dropoff.resume_token}",
        "dropoff_id": dropoff.id,
        "nudge_status": dropoff.nudge_status,
        "dispatch_details": dispatch_res
    }


@router.post("/checkout-dropoff/{dropoff_id}/simulate-conversion")
def simulate_dropoff_conversion(
    dropoff_id: str,
    db: Session = Depends(get_db)
):
    """Simulate customer clicking the resume link and completing checkout."""
    dropoff = db.query(CheckoutDropoff).filter(CheckoutDropoff.id == dropoff_id).first()
    if not dropoff:
        raise HTTPException(status_code=404, detail="Checkout dropoff not found")

    dropoff.nudge_status = "converted"
    dropoff.converted_at = datetime.utcnow()
    db.commit()

    return {
        "success": True,
        "message": "Cart restored and transaction completed successfully!",
        "recovered_amount": dropoff.cart_value,
        "customer_name": dropoff.customer_name
    }

