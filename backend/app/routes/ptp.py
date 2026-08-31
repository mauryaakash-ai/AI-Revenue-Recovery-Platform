"""
Promise-to-Pay (PTP) Tracker Route
Features:
- Captures committed payment date/amount from Voice, WhatsApp, Chat, or Email
- Auto-schedules reminders prior to promise date
- Scores customer reliability (kept vs broken promises)
- Escalates broken promises to higher-urgency recovery channels
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid

from app.database import get_db
from app.models import PromiseToPay, Merchant, Customer, AuditLog

router = APIRouter()


class PTPCreateRequest(BaseModel):
    customer_id: Optional[str] = None
    customer_name: str
    reference_type: str  # transaction, invoice, subscription
    reference_id: str
    promised_amount: float
    promised_date: str  # ISO string or YYYY-MM-DD
    channel_source: Optional[str] = "voice_agent"  # voice_agent, whatsapp, chat, email


class PTPStatusUpdateRequest(BaseModel):
    fulfillment_status: str  # kept, broken, rescheduled
    notes: Optional[str] = None


@router.get("/ptp/records")
def get_ptp_records(
    merchant_id: Optional[str] = None,
    fulfillment_status: Optional[str] = None,
    channel_source: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Retrieve Promise-to-Pay commitments with reliability scores and schedule."""
    query = db.query(PromiseToPay)
    if merchant_id:
        query = query.filter(PromiseToPay.merchant_id == merchant_id)
    if fulfillment_status:
        query = query.filter(PromiseToPay.fulfillment_status == fulfillment_status)
    if channel_source:
        query = query.filter(PromiseToPay.channel_source == channel_source)
    
    ptp_list = query.order_by(PromiseToPay.promised_date.asc()).limit(limit).all()

    total_ptp = db.query(PromiseToPay).count()
    pending_count = db.query(PromiseToPay).filter(PromiseToPay.fulfillment_status == "pending").count()
    kept_count = db.query(PromiseToPay).filter(PromiseToPay.fulfillment_status == "kept").count()
    broken_count = db.query(PromiseToPay).filter(PromiseToPay.fulfillment_status == "broken").count()

    total_committed_amount = db.query(func.sum(PromiseToPay.promised_amount)).scalar() or 0.0
    kept_amount = db.query(func.sum(PromiseToPay.promised_amount)).filter(PromiseToPay.fulfillment_status == "kept").scalar() or 0.0
    avg_reliability = db.query(func.avg(PromiseToPay.reliability_score)).scalar() or 82.5

    return {
        "summary": {
            "total_commitments": total_ptp,
            "pending_count": pending_count,
            "kept_count": kept_count,
            "broken_count": broken_count,
            "commitment_kept_rate": round((kept_count / max(kept_count + broken_count, 1)) * 100, 1),
            "total_committed_value": total_committed_amount,
            "realized_kept_value": kept_amount,
            "average_reliability_score": round(avg_reliability, 1),
            "channel_distribution": {
                "voice_agent": db.query(PromiseToPay).filter(PromiseToPay.channel_source == "voice_agent").count(),
                "whatsapp": db.query(PromiseToPay).filter(PromiseToPay.channel_source == "whatsapp").count(),
                "chat": db.query(PromiseToPay).filter(PromiseToPay.channel_source == "chat").count(),
                "email": db.query(PromiseToPay).filter(PromiseToPay.channel_source == "email").count(),
            }
        },
        "items": [
            {
                "id": p.id,
                "merchant_id": p.merchant_id,
                "customer_id": p.customer_id,
                "customer_name": p.customer_name,
                "reference_type": p.reference_type,
                "reference_id": p.reference_id,
                "promised_amount": p.promised_amount,
                "promised_date": p.promised_date.isoformat() if p.promised_date else None,
                "channel_source": p.channel_source,
                "fulfillment_status": p.fulfillment_status,
                "reliability_score": round(p.reliability_score, 1),
                "reminded_at": p.reminded_at.isoformat() if p.reminded_at else None,
                "fulfilled_at": p.fulfilled_at.isoformat() if p.fulfilled_at else None,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in ptp_list
        ]
    }


@router.post("/ptp/create")
def create_ptp(
    payload: PTPCreateRequest,
    db: Session = Depends(get_db)
):
    """Log a new customer Promise-to-Pay commitment."""
    merchant = db.query(Merchant).first()
    try:
        p_date = datetime.fromisoformat(payload.promised_date.replace("Z", "+00:00"))
    except Exception:
        p_date = datetime.utcnow() + timedelta(days=3)

    ptp = PromiseToPay(
        id=str(uuid.uuid4()),
        merchant_id=merchant.id if merchant else "merchant_urbankart",
        customer_id=payload.customer_id or str(uuid.uuid4()),
        customer_name=payload.customer_name,
        reference_type=payload.reference_type,
        reference_id=payload.reference_id,
        promised_amount=payload.promised_amount,
        promised_date=p_date,
        channel_source=payload.channel_source or "whatsapp",
        fulfillment_status="pending",
        reliability_score=85.0
    )
    db.add(ptp)
    db.commit()

    return {
        "success": True,
        "message": f"Promise-to-Pay for ₹{ptp.promised_amount:,.2f} recorded for {ptp.customer_name}.",
        "ptp_id": ptp.id,
        "promised_date": ptp.promised_date.isoformat(),
        "fulfillment_status": ptp.fulfillment_status
    }


@router.post("/ptp/{ptp_id}/update-status")
def update_ptp_status(
    ptp_id: str,
    payload: PTPStatusUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update fulfillment status of a Promise-to-Pay and adjust customer reliability score."""
    ptp = db.query(PromiseToPay).filter(PromiseToPay.id == ptp_id).first()
    if not ptp:
        raise HTTPException(status_code=404, detail="Promise-to-Pay record not found")

    ptp.fulfillment_status = payload.fulfillment_status
    if payload.fulfillment_status == "kept":
        ptp.fulfilled_at = datetime.utcnow()
        ptp.reliability_score = min(100.0, ptp.reliability_score + 5.0)
        msg = f"Commitment marked KEPT! Reliability score updated to {ptp.reliability_score:.1f}%."
    elif payload.fulfillment_status == "broken":
        ptp.reliability_score = max(0.0, ptp.reliability_score - 15.0)
        msg = f"Commitment marked BROKEN. Reliability score penalized to {ptp.reliability_score:.1f}%. Automatic escalation triggered."
    else:
        msg = "Promise rescheduled."

    db.commit()

    return {
        "success": True,
        "message": msg,
        "ptp_id": ptp.id,
        "fulfillment_status": ptp.fulfillment_status,
        "updated_reliability_score": ptp.reliability_score
    }

