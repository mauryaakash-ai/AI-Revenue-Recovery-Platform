"""
Hinglish AI Voice Recovery & Call Simulator Route
Features:
- Outbound IVR & AI Voice Agent call tracking
- Code-switched Hinglish (Hindi-English) conversation transcripts
- Real-time customer objection extraction (salary_pending, retry_link_needed, etc.)
- Automatic sync with Promise-to-Pay (PTP) tracker
- Interactive call simulation with bilingual audio synthesis previews
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid

from app.database import get_db
from app.models import VoiceCallLog, PromiseToPay, Merchant, Customer, AuditLog

router = APIRouter()


class VoiceCallSimulateRequest(BaseModel):
    customer_phone: str
    customer_name: str
    amount: float
    reference_type: Optional[str] = "transaction"  # transaction, invoice, subscription
    reference_id: Optional[str] = "TXN_SIM_001"
    customer_objection: Optional[str] = "salary_pending"  # salary_pending, retry_link_needed, will_pay_online


@router.get("/voice/calls")
def get_voice_calls(
    merchant_id: Optional[str] = None,
    call_status: Optional[str] = None,
    objection: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Retrieve voice recovery call logs, audio transcripts, and extracted PTP dates."""
    query = db.query(VoiceCallLog)
    if merchant_id:
        query = query.filter(VoiceCallLog.merchant_id == merchant_id)
    if call_status:
        query = query.filter(VoiceCallLog.call_status == call_status)
    if objection:
        query = query.filter(VoiceCallLog.detected_objection == objection)
    
    calls = query.order_by(VoiceCallLog.created_at.desc()).limit(limit).all()

    total_calls = db.query(VoiceCallLog).count()
    completed_calls = db.query(VoiceCallLog).filter(VoiceCallLog.call_status == "completed").count()
    ptp_captured_count = db.query(VoiceCallLog).filter(VoiceCallLog.captured_ptp_date.isnot(None)).count()
    ptp_captured_value = db.query(func.sum(VoiceCallLog.captured_ptp_amount)).scalar() or 0.0

    return {
        "summary": {
            "total_calls_initiated": total_calls,
            "completed_calls": completed_calls,
            "call_completion_rate": round((completed_calls / max(total_calls, 1)) * 100, 1),
            "ptp_captured_count": ptp_captured_count,
            "ptp_captured_value": ptp_captured_value,
            "objection_distribution": {
                "salary_pending": db.query(VoiceCallLog).filter(VoiceCallLog.detected_objection == "salary_pending").count(),
                "retry_link_needed": db.query(VoiceCallLog).filter(VoiceCallLog.detected_objection == "retry_link_needed").count(),
                "will_pay_online": db.query(VoiceCallLog).filter(VoiceCallLog.detected_objection == "will_pay_online").count(),
                "disputed_amount": db.query(VoiceCallLog).filter(VoiceCallLog.detected_objection == "disputed_amount").count(),
            }
        },
        "items": [
            {
                "id": c.id,
                "merchant_id": c.merchant_id,
                "customer_id": c.customer_id,
                "customer_name": c.customer_name,
                "customer_phone": c.customer_phone,
                "call_sid": c.call_sid,
                "language": c.language,
                "duration_seconds": c.duration_seconds,
                "call_status": c.call_status,
                "transcript_hinglish": c.transcript_hinglish,
                "transcript_english": c.transcript_english,
                "detected_intent": c.detected_intent,
                "detected_objection": c.detected_objection,
                "captured_ptp_date": c.captured_ptp_date.isoformat() if c.captured_ptp_date else None,
                "captured_ptp_amount": c.captured_ptp_amount,
                "audio_simulation_url": c.audio_simulation_url,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in calls
        ]
    }


@router.post("/voice/simulate-call")
def simulate_voice_call(
    payload: VoiceCallSimulateRequest,
    db: Session = Depends(get_db)
):
    """
    Launch interactive Hinglish AI Voice Call Simulator.
    Simulates code-switched conversation, extracts payment intent, and logs PTP commitment.
    """
    merchant = db.query(Merchant).first()
    customer = db.query(Customer).filter(Customer.name == payload.customer_name).first() or db.query(Customer).first()

    ptp_target_date = datetime.utcnow() + timedelta(days=3)
    call_sid = f"CA_{uuid.uuid4().hex[:12]}"

    if payload.customer_objection == "salary_pending":
        hinglish_dialogue = (
            f"AI: Namaste {payload.customer_name} ji! Main Razorpay Automated Recovery Assistant bol raha hoon. "
            f"Aapka ₹{payload.amount:,.2f} ka payment bank timeout ki wajah se complete nahi ho paya tha. Kya aap abhi retry karna chahenge?\n"
            f"Customer: Haan actually abhi salary aani baaki hai. Main Friday ko pakka pay kar dunga.\n"
            f"AI: Bilkul samajh gaya ji! Humne aapka Promise-to-Pay 3 din baad ke liye record kar liya hai. "
            f"Hum aapko Friday morning WhatsApp par convenient 1-click UPI link bhej denge. Dhanyawad!"
        )
        english_dialogue = (
            f"AI: Hello {payload.customer_name}! This is Razorpay Automated Recovery Assistant. "
            f"Your payment of ₹{payload.amount:,.2f} was interrupted due to a bank timeout. Would you like to retry now?\n"
            f"Customer: Actually my salary is pending. I will definitely pay on Friday.\n"
            f"AI: Completely understood! We have recorded your Promise-to-Pay for Friday. "
            f"We will share a convenient 1-click UPI link on WhatsApp on Friday morning. Thank you!"
        )
        intent = "Customer committed to pay on salary credit date"
    elif payload.customer_objection == "retry_link_needed":
        hinglish_dialogue = (
            f"AI: Namaste {payload.customer_name} ji! Aapka checkout transaction decline ho gaya tha. Kya main aapko WhatsApp par direct payment link send karoon?\n"
            f"Customer: Haan please WhatsApp par bhej dijiye, card se OTP nahi aa raha tha. Main UPI se turant kar dunga.\n"
            f"AI: Ji bilkul, WhatsApp link successfully bhej diya gaya hai. Aap 1-click mein complete kar sakte hain!"
        )
        english_dialogue = (
            f"AI: Hello {payload.customer_name}! Your transaction was declined. Shall I send a direct payment link to your WhatsApp?\n"
            f"Customer: Yes please send it on WhatsApp, card OTP was failing. I'll pay instantly via UPI.\n"
            f"AI: Certainly, the WhatsApp link has been sent. You can complete it in one click!"
        )
        intent = "Customer requested instant UPI link on WhatsApp"
    else:
        hinglish_dialogue = (
            f"AI: Namaste {payload.customer_name} ji! Razorpay team se follow-up call hai aapke pending transaction ke regarding.\n"
            f"Customer: Theek hai, main online login karke abhi clear kar deta hoon.\n"
            f"AI: Shuru karne ke liye dhanyawad! Have a great day."
        )
        english_dialogue = (
            f"AI: Hello {payload.customer_name}! This is a follow-up call from Razorpay regarding your pending transaction.\n"
            f"Customer: Okay, I will log in online and clear it right away.\n"
            f"AI: Thank you for your confirmation! Have a great day."
        )
        intent = "Customer confirmed online self-service clearance"

    # Create Voice Call Record
    call_log = VoiceCallLog(
        id=str(uuid.uuid4()),
        merchant_id=merchant.id if merchant else "merchant_urbankart",
        customer_id=customer.id if customer else None,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        call_sid=call_sid,
        language="hinglish",
        duration_seconds=52,
        call_status="completed",
        transcript_hinglish=hinglish_dialogue,
        transcript_english=english_dialogue,
        detected_intent=intent,
        detected_objection=payload.customer_objection or "salary_pending",
        captured_ptp_date=ptp_target_date,
        captured_ptp_amount=payload.amount,
        audio_simulation_url="https://assets.razorpay.com/voice-simulations/sample_hinglish_01.mp3"
    )
    db.add(call_log)

    # Auto sync with Promise-to-Pay (PTP) tracker
    ptp = PromiseToPay(
        id=str(uuid.uuid4()),
        merchant_id=merchant.id if merchant else "merchant_urbankart",
        customer_id=customer.id if customer else str(uuid.uuid4()),
        customer_name=payload.customer_name,
        reference_type=payload.reference_type or "transaction",
        reference_id=payload.reference_id or "TXN_SIM_001",
        promised_amount=payload.amount,
        promised_date=ptp_target_date,
        channel_source="voice_agent",
        fulfillment_status="pending",
        reliability_score=customer.historical_recovery_rate * 100 if customer else 85.0
    )
    db.add(ptp)
    db.commit()

    return {
        "success": True,
        "message": "Hinglish AI Voice Call completed successfully and PTP commitment synced.",
        "call_sid": call_sid,
        "call_log_id": call_log.id,
        "ptp_id": ptp.id,
        "transcript_hinglish": hinglish_dialogue,
        "transcript_english": english_dialogue,
        "detected_intent": intent,
        "captured_ptp_date": ptp_target_date.isoformat(),
        "captured_ptp_amount": payload.amount
    }

