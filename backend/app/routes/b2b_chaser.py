"""
B2B Receivables Chaser & Invoice Recovery Route
Features:
- Prioritized chase queue by expected recovery value ($Amount \times Probability$) & DPD
- Staged escalating reminders (Friendly Nudge -> Formal Notice -> Involve Account Owner -> Collections)
- Auto-generated payment links and Statement-of-Account (SOA)
- Human & Collections agency handoff workflows
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid

from app.database import get_db
from app.models import B2BInvoice, B2BReminder, Merchant, AuditLog

router = APIRouter()


class ReminderRequest(BaseModel):
    stage: str  # friendly_nudge, formal_notice, account_owner_escalation, collections_handoff
    channel: Optional[str] = "email"  # email, whatsapp, phone_call
    custom_note: Optional[str] = None


@router.get("/b2b-chaser/invoices")
def get_b2b_invoices(
    merchant_id: Optional[str] = None,
    risk_tier: Optional[str] = None,
    status: Optional[str] = None,
    stage: Optional[str] = None,
    min_dpd: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Retrieve B2B overdue invoices prioritized by expected recovery value."""
    query = db.query(B2BInvoice)
    if merchant_id:
        query = query.filter(B2BInvoice.merchant_id == merchant_id)
    if risk_tier:
        query = query.filter(B2BInvoice.risk_tier == risk_tier)
    if status:
        query = query.filter(B2BInvoice.status == status)
    if stage:
        query = query.filter(B2BInvoice.current_stage == stage)
    if min_dpd is not None:
        query = query.filter(B2BInvoice.days_past_due >= min_dpd)
    
    invoices = query.order_by((B2BInvoice.amount * B2BInvoice.expected_recovery_prob).desc()).limit(limit).all()

    # Calculate summary metrics and aging buckets
    total_outstanding = db.query(func.sum(B2BInvoice.amount)).filter(B2BInvoice.status == "pending").scalar() or 0.0
    total_settled = db.query(func.sum(B2BInvoice.amount)).filter(B2BInvoice.status == "settled").scalar() or 0.0
    pending_count = db.query(B2BInvoice).filter(B2BInvoice.status == "pending").count()

    bucket_0_30 = db.query(func.sum(B2BInvoice.amount)).filter(B2BInvoice.days_past_due <= 30, B2BInvoice.status == "pending").scalar() or 0.0
    bucket_31_60 = db.query(func.sum(B2BInvoice.amount)).filter(B2BInvoice.days_past_due > 30, B2BInvoice.days_past_due <= 60, B2BInvoice.status == "pending").scalar() or 0.0
    bucket_61_90 = db.query(func.sum(B2BInvoice.amount)).filter(B2BInvoice.days_past_due > 60, B2BInvoice.days_past_due <= 90, B2BInvoice.status == "pending").scalar() or 0.0
    bucket_90_plus = db.query(func.sum(B2BInvoice.amount)).filter(B2BInvoice.days_past_due > 90, B2BInvoice.status == "pending").scalar() or 0.0

    return {
        "summary": {
            "total_outstanding_amount": total_outstanding,
            "total_settled_amount": total_settled,
            "pending_invoice_count": pending_count,
            "aging_buckets": {
                "0_30_dpd": bucket_0_30,
                "31_60_dpd": bucket_31_60,
                "61_90_dpd": bucket_61_90,
                "90_plus_dpd": bucket_90_plus
            },
            "risk_distribution": {
                "critical": db.query(B2BInvoice).filter(B2BInvoice.risk_tier == "critical", B2BInvoice.status == "pending").count(),
                "high": db.query(B2BInvoice).filter(B2BInvoice.risk_tier == "high", B2BInvoice.status == "pending").count(),
                "medium": db.query(B2BInvoice).filter(B2BInvoice.risk_tier == "medium", B2BInvoice.status == "pending").count(),
                "low": db.query(B2BInvoice).filter(B2BInvoice.risk_tier == "low", B2BInvoice.status == "pending").count(),
            }
        },
        "items": [
            {
                "id": inv.id,
                "merchant_id": inv.merchant_id,
                "invoice_number": inv.invoice_number,
                "buyer_name": inv.buyer_name,
                "buyer_email": inv.buyer_email,
                "buyer_phone": inv.buyer_phone,
                "buyer_gstin": inv.buyer_gstin,
                "amount": inv.amount,
                "due_date": inv.due_date.isoformat() if inv.due_date else None,
                "days_past_due": inv.days_past_due,
                "risk_tier": inv.risk_tier,
                "payment_terms": inv.payment_terms,
                "expected_recovery_prob": round(inv.expected_recovery_prob * 100, 1),
                "expected_recovery_value": round(inv.amount * inv.expected_recovery_prob, 2),
                "current_stage": inv.current_stage,
                "settlement_link": inv.settlement_link,
                "status": inv.status,
                "created_at": inv.created_at.isoformat() if inv.created_at else None,
                "settled_at": inv.settled_at.isoformat() if inv.settled_at else None
            }
            for inv in invoices
        ]
    }


@router.post("/b2b-chaser/{invoice_id}/send-reminder")
def send_b2b_reminder(
    invoice_id: str,
    payload: ReminderRequest,
    db: Session = Depends(get_db)
):
    """Dispatch staged reminder with payment link and Statement-of-Account."""
    inv = db.query(B2BInvoice).filter(B2BInvoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="B2B Invoice not found")

    inv.current_stage = payload.stage
    reminder = B2BReminder(
        id=str(uuid.uuid4()),
        invoice_id=inv.id,
        stage=payload.stage,
        channel=payload.channel or "email",
        recipient=inv.buyer_email,
        subject_or_template=f"Statement & Payment Reminder for Invoice {inv.invoice_number}",
        content_preview=f"Dear {inv.buyer_name}, this is a reminder regarding overdue invoice {inv.invoice_number} (₹{inv.amount:,.2f}). Please pay via: {inv.settlement_link}",
        status="sent"
    )
    db.add(reminder)

    # If stage is collections handoff, update status
    if payload.stage == "collections_handoff":
        inv.status = "in_collections"

    db.commit()

    # Dispatch live notification via communication dispatcher
    from app.communication_service import dispatcher
    dispatch_res = dispatcher.send_invoice_reminder(
        buyer_name=inv.buyer_name,
        invoice_number=inv.invoice_number,
        amount=inv.amount,
        settlement_link=inv.settlement_link or f"https://rzp.io/l/inv_{inv.invoice_number}",
        stage=payload.stage
    )

    return {
        "success": True,
        "message": f"Reminder stage '{payload.stage}' sent to {inv.buyer_name} via {payload.channel or 'email'}.",
        "invoice_number": inv.invoice_number,
        "settlement_link": inv.settlement_link,
        "current_stage": inv.current_stage,
        "dispatch_details": dispatch_res
    }


@router.post("/b2b-chaser/{invoice_id}/settle")
def settle_b2b_invoice(
    invoice_id: str,
    db: Session = Depends(get_db)
):
    """Mark an invoice as settled / paid in full."""
    inv = db.query(B2BInvoice).filter(B2BInvoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="B2B Invoice not found")

    inv.status = "settled"
    inv.settled_at = datetime.utcnow()
    db.commit()

    return {
        "success": True,
        "message": f"Invoice {inv.invoice_number} settled successfully!",
        "settled_amount": inv.amount,
        "buyer_name": inv.buyer_name
    }

