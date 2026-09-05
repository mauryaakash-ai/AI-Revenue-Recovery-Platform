"""
Payment Gateway Webhook Endpoints
Endpoints:
- POST /api/v1/webhooks/razorpay
- POST /api/v1/webhooks/stripe
- POST /api/v1/webhooks/generic
- GET  /api/v1/webhooks/events
- POST /api/v1/webhooks/simulate
"""

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import uuid

from app.database import get_db
from app.models import WebhookEvent, Merchant
from app.webhook_service import webhook_engine, WebhookVerificationError, WebhookDuplicateError

router = APIRouter()


class WebhookSimulationRequest(BaseModel):
    provider: str = "razorpay"  # razorpay, stripe, generic
    amount: float = 18500.0
    customer_email: Optional[str] = "ananya.patel@example.com"
    customer_phone: Optional[str] = "+91 98201 94821"
    failure_reason: Optional[str] = "Bank connection timed out during 3DS OTP verification"
    failure_code: Optional[str] = "BAD_REQUEST_PAYMENT_TIMED_OUT"
    merchant_id: Optional[str] = "merchant_urbankart"


@router.post("/webhooks/razorpay")
async def handle_razorpay_webhook(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Handle incoming Razorpay payment events with HMAC signature validation"""
    raw_body = await request.body()
    merchant = db.query(Merchant).first()
    merchant_id = merchant.id if merchant else "merchant_urbankart"

    try:
        result = webhook_engine.process_webhook(
            provider="razorpay",
            raw_body=raw_body,
            signature=x_razorpay_signature,
            merchant_id=merchant_id,
            db=db
        )
        return result
    except WebhookVerificationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/webhooks/stripe")
async def handle_stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Handle incoming Stripe payment events with signature validation"""
    raw_body = await request.body()
    merchant = db.query(Merchant).first()
    merchant_id = merchant.id if merchant else "merchant_urbankart"

    try:
        result = webhook_engine.process_webhook(
            provider="stripe",
            raw_body=raw_body,
            signature=stripe_signature,
            merchant_id=merchant_id,
            db=db
        )
        return result
    except WebhookVerificationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/webhooks/generic")
async def handle_generic_webhook(
    request: Request,
    x_webhook_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Generic payment gateway webhook intake"""
    raw_body = await request.body()
    merchant = db.query(Merchant).first()
    merchant_id = merchant.id if merchant else "merchant_urbankart"

    try:
        result = webhook_engine.process_webhook(
            provider="generic",
            raw_body=raw_body,
            signature=x_webhook_signature,
            merchant_id=merchant_id,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/webhooks/events")
def get_webhook_events(
    merchant_id: Optional[str] = None,
    provider: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Retrieve historical raw webhook events ledger with deduplication status"""
    query = db.query(WebhookEvent)
    if merchant_id:
        query = query.filter(WebhookEvent.merchant_id == merchant_id)
    if provider:
        query = query.filter(WebhookEvent.provider == provider)
    if status:
        query = query.filter(WebhookEvent.status == status)

    events = query.order_by(WebhookEvent.received_at.desc()).limit(limit).all()

    total_count = db.query(WebhookEvent).count()
    processed_count = db.query(WebhookEvent).filter(WebhookEvent.status == "processed").count()
    duplicate_count = db.query(WebhookEvent).filter(WebhookEvent.status == "duplicate").count()

    return {
        "summary": {
            "total_webhooks_received": total_count,
            "processed": processed_count,
            "duplicates_prevented": duplicate_count,
            "success_rate": round((processed_count / max(total_count, 1)) * 100, 1)
        },
        "items": [
            {
                "id": e.id,
                "merchant_id": e.merchant_id,
                "provider": e.provider,
                "event_type": e.event_type,
                "event_id": e.event_id,
                "idempotency_key": e.idempotency_key,
                "status": e.status,
                "normalized_transaction_id": e.normalized_transaction_id,
                "received_at": e.received_at.isoformat() if e.received_at else None,
                "processed_at": e.processed_at.isoformat() if e.processed_at else None
            }
            for e in events
        ]
    }


@router.post("/webhooks/simulate")
def simulate_webhook(
    payload: WebhookSimulationRequest,
    db: Session = Depends(get_db)
):
    """
    Simulate an incoming failed payment webhook to test pipeline trigger & idempotency
    """
    merchant = db.query(Merchant).filter(Merchant.id == payload.merchant_id).first() or db.query(Merchant).first()
    merchant_id = merchant.id if merchant else "merchant_urbankart"

    if payload.provider == "razorpay":
        sample_body = {
            "entity": "event",
            "account_id": "acc_razorpay_urbankart",
            "event": "payment.failed",
            "contains": ["payment"],
            "payload": {
                "payment": {
                    "entity": {
                        "id": f"pay_{uuid.uuid4().hex[:14]}",
                        "amount": int(payload.amount * 100),
                        "currency": "INR",
                        "status": "failed",
                        "order_id": f"order_{uuid.uuid4().hex[:14]}",
                        "method": "upi",
                        "email": payload.customer_email,
                        "contact": payload.customer_phone,
                        "error_code": payload.failure_code,
                        "error_description": payload.failure_reason,
                        "bank": "HDFC Bank"
                    }
                }
            }
        }
    elif payload.provider == "stripe":
        sample_body = {
            "id": f"evt_{uuid.uuid4().hex[:14]}",
            "object": "event",
            "type": "payment_intent.payment_failed",
            "data": {
                "object": {
                    "id": f"pi_{uuid.uuid4().hex[:14]}",
                    "amount": int(payload.amount * 100),
                    "currency": "usd",
                    "status": "requires_payment_method",
                    "receipt_email": payload.customer_email,
                    "last_payment_error": {
                        "code": payload.failure_code,
                        "decline_code": "insufficient_funds",
                        "message": payload.failure_reason
                    }
                }
            }
        }
    else:
        sample_body = {
            "provider": "generic",
            "event_type": "payment.failed",
            "payment_id": f"gen_pay_{uuid.uuid4().hex[:10]}",
            "order_id": f"gen_ord_{uuid.uuid4().hex[:10]}",
            "amount": payload.amount,
            "currency": "INR",
            "payment_method": "upi",
            "bank_name": "State Bank of India",
            "customer_email": payload.customer_email,
            "customer_phone": payload.customer_phone,
            "failure_code": payload.failure_code,
            "failure_reason": payload.failure_reason,
            "failure_type": "temporary"
        }

    raw_bytes = json.dumps(sample_body).encode("utf-8")
    result = webhook_engine.process_webhook(
        provider=payload.provider,
        raw_body=raw_bytes,
        signature="simulated_test_sig",
        merchant_id=merchant_id,
        db=db
    )
    return result

