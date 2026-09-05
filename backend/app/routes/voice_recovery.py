"""
Hinglish AI Voice Recovery & Call Simulator Route
Features:
- Multi-Persona Neural Voice Pipeline (Priya, Rahul, Swara, Madhur, Kavya)
- Audio Call Recording tracking and playback across all call history
- Outbound Calling Queue for Pending and Failed transactions
- Dynamic DTMF interactive response with male/female voice acknowledgements
- Real-time customer objection extraction & Promise-to-Pay (PTP) synchronization
- Zero-cost WebRTC softphone telephony integration
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.models import (
    VoiceCallLog, PromiseToPay, Merchant, Customer, AuditLog,
    Transaction, TransactionStatus, RecoveryOpportunity
)

router = APIRouter()

# 5 Studio-Grade Indian Neural Voice Personas
PERSONAS = {
    "priya": {
        "id": "priya",
        "name": "Priya",
        "gender": "female",
        "title": "Priority Care Specialist",
        "voice_model": "en-IN-NeerjaExpressiveNeural",
        "badge": "Studio Neural HD",
        "description": "Expressive, polite recovery specialist with natural Indian customer care cadence."
    },
    "rahul": {
        "id": "rahul",
        "name": "Rahul",
        "gender": "male",
        "title": "Enterprise Recovery Lead",
        "voice_model": "en-IN-PrabhatNeural",
        "badge": "Warm Professional",
        "description": "Authoritative, reassuring male voice tailored for high-ticket transaction recovery."
    },
    "swara": {
        "id": "swara",
        "name": "Swara",
        "gender": "female",
        "title": "Bilingual Hinglish Specialist",
        "voice_model": "hi-IN-SwaraNeural",
        "badge": "Natural Hinglish",
        "description": "Conversational Hindi/English agent ideal for mandate failures and tier-2/3 demographics."
    },
    "madhur": {
        "id": "madhur",
        "name": "Madhur",
        "gender": "male",
        "title": "Support & Gateway Lead",
        "voice_model": "hi-IN-MadhurNeural",
        "badge": "Reassuring Tone",
        "description": "Calm, supportive agent specialized in bank timeout and network error follow-ups."
    },
    "kavya": {
        "id": "kavya",
        "name": "Kavya",
        "gender": "female",
        "title": "Customer Resolution Desk",
        "voice_model": "mr-IN-AarohiNeural",
        "badge": "Melodious Clarity",
        "description": "Soft, empathetic tone for checkout drop-offs and gentle payment reminders."
    }
}


class VoiceCallSimulateRequest(BaseModel):
    customer_phone: str
    customer_name: str
    amount: float
    reference_type: Optional[str] = "transaction"
    reference_id: Optional[str] = "TXN_SIM_001"
    customer_objection: Optional[str] = "salary_pending"
    voice_persona: Optional[str] = "priya"


class VoiceCallDispatchRequest(BaseModel):
    phone_number: str
    customer_name: Optional[str] = "Valued Customer"
    amount: Optional[float] = 14500.0
    scenario: Optional[str] = "payment_retry"  # payment_retry, salary_pending, mandate_failure, failed_call, pending_call, custom
    custom_script: Optional[str] = None
    language: Optional[str] = "hinglish"
    provider: Optional[str] = "free_webrtc_softphone"
    voice_persona: Optional[str] = "priya"  # priya, rahul, swara, madhur, kavya
    transaction_id: Optional[str] = None


class DTMFPayload(BaseModel):
    call_sid: str
    digit: str  # 1, 2, 3
    customer_phone: Optional[str] = None
    customer_name: Optional[str] = "Valued Customer"
    amount: Optional[float] = 14500.0
    voice_persona: Optional[str] = "priya"


class CallStatusUpdateRequest(BaseModel):
    call_sid: str
    call_status: str  # completed, failed_unreachable, recovered, ptp_committed, pending_retry
    duration_seconds: Optional[int] = None
    notes: Optional[str] = None


@router.get("/voice/personas")
def get_voice_personas():
    """Returns available studio-grade neural voice personas."""
    return {
        "count": len(PERSONAS),
        "personas": list(PERSONAS.values())
    }


@router.get("/voice/calling-queue")
def get_voice_calling_queue(
    status_filter: Optional[str] = "all",  # all, failed, pending, recovered, ptp
    search: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Returns the real-time Outbound Calling Queue categorized by Pending and Failed transactions.
    Enables agents/system to initiate voice recovery calls with 1 click.
    """
    query = db.query(Transaction).join(Customer)

    if status_filter == "failed":
        query = query.filter(Transaction.status == TransactionStatus.FAILED)
    elif status_filter == "pending":
        query = query.filter(Transaction.status == TransactionStatus.PENDING)
    else:
        query = query.filter(Transaction.status.in_([TransactionStatus.FAILED, TransactionStatus.PENDING]))

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Customer.name.ilike(search_pattern)) | 
            (Customer.phone.ilike(search_pattern)) |
            (Transaction.id.ilike(search_pattern))
        )

    # Sort high-value transactions first
    transactions = query.order_by(desc(Transaction.amount)).limit(limit).all()

    # Preload recent call logs to map last call status
    call_logs = db.query(VoiceCallLog).order_by(desc(VoiceCallLog.created_at)).limit(200).all()
    call_map_by_phone = {}
    call_map_by_txn = {}
    for cl in call_logs:
        if cl.transaction_id and cl.transaction_id not in call_map_by_txn:
            call_map_by_txn[cl.transaction_id] = cl
        if cl.customer_phone and cl.customer_phone not in call_map_by_phone:
            call_map_by_phone[cl.customer_phone] = cl

    queue_items = []
    for tx in transactions:
        cust = tx.customer
        cust_name = cust.name if cust else "Valued Customer"
        cust_phone = cust.phone if cust else "+91 9876543210"
        tx_status = tx.status.value if hasattr(tx.status, "value") else str(tx.status).lower()

        # Find any matching prior call
        prior_call = call_map_by_txn.get(tx.id) or call_map_by_phone.get(cust_phone)

        # Dynamic Recommendation Engine for Scenario & Persona
        amt = tx.amount or 0.0
        reason = (tx.failure_reason or "").lower()

        if tx_status == "pending":
            if "mandate" in reason:
                rec_scenario = "mandate_failure"
                rec_persona = "swara"
            else:
                rec_scenario = "pending_call"
                rec_persona = "priya" if amt < 25000 else "rahul"
        else:
            if "insufficient" in reason or "salary" in reason:
                rec_scenario = "salary_pending"
                rec_persona = "priya"
            elif "mandate" in reason:
                rec_scenario = "mandate_failure"
                rec_persona = "swara"
            elif "timeout" in reason or "network" in reason:
                rec_scenario = "payment_retry"
                rec_persona = "madhur" if amt < 20000 else "rahul"
            else:
                rec_scenario = "failed_call"
                rec_persona = "rahul" if amt > 30000 else "kavya"

        # Determine Call Status
        if prior_call:
            current_call_status = prior_call.call_status
            last_called_at = prior_call.created_at.isoformat() if prior_call.created_at else None
            recording_url = prior_call.audio_simulation_url
        else:
            current_call_status = "uncalled"
            last_called_at = None
            recording_url = None

        queue_items.append({
            "transaction_id": tx.id,
            "customer_id": cust.id if cust else None,
            "customer_name": cust_name,
            "customer_phone": cust_phone,
            "customer_segment": cust.segment if cust else "standard",
            "amount": amt,
            "currency": tx.currency or "INR",
            "payment_method": tx.payment_method or "upi",
            "bank_name": tx.bank_name or "HDFC Bank",
            "transaction_status": tx_status.upper(),
            "failure_reason": tx.failure_reason or ("Bank Timeout" if tx_status == "failed" else "Pending Authorization"),
            "failure_code": tx.failure_code or "AUTH_TIMEOUT",
            "failure_type": tx.failure_type or "temporary",
            "risk_score": tx.risk_score or 0.12,
            "urgency": "CRITICAL" if amt > 35000 else "HIGH" if amt > 15000 else "MEDIUM",
            "recommended_scenario": rec_scenario,
            "recommended_persona": rec_persona,
            "current_call_status": current_call_status,
            "last_called_at": last_called_at,
            "recording_url": recording_url
        })

    # Aggregated Summary
    total_failed = db.query(Transaction).filter(Transaction.status == TransactionStatus.FAILED).count()
    total_pending = db.query(Transaction).filter(Transaction.status == TransactionStatus.PENDING).count()
    total_at_risk = db.query(func.sum(Transaction.amount)).filter(
        Transaction.status.in_([TransactionStatus.FAILED, TransactionStatus.PENDING])
    ).scalar() or 0.0

    recovered_calls_count = db.query(VoiceCallLog).filter(VoiceCallLog.call_status == "recovered").count()
    ptp_calls_count = db.query(VoiceCallLog).filter(VoiceCallLog.call_status == "ptp_committed").count()

    return {
        "summary": {
            "total_at_risk_amount": total_at_risk,
            "failed_transactions_count": total_failed,
            "pending_transactions_count": total_pending,
            "total_in_queue": len(queue_items),
            "recovered_calls_count": recovered_calls_count,
            "ptp_calls_count": ptp_calls_count
        },
        "items": queue_items
    }


@router.get("/voice/calls")
def get_voice_calls(
    merchant_id: Optional[str] = None,
    call_status: Optional[str] = None,
    objection: Optional[str] = None,
    voice_persona: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Retrieve voice recovery call audit records with full playable Call Recordings,
    persona details, transcripts, and status tags.
    """
    query = db.query(VoiceCallLog)

    if merchant_id:
        query = query.filter(VoiceCallLog.merchant_id == merchant_id)
    if call_status and call_status != "all":
        query = query.filter(VoiceCallLog.call_status == call_status)
    if objection:
        query = query.filter(VoiceCallLog.detected_objection == objection)
    if voice_persona and voice_persona != "all":
        query = query.filter(VoiceCallLog.voice_persona == voice_persona)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (VoiceCallLog.customer_name.ilike(search_pattern)) |
            (VoiceCallLog.customer_phone.ilike(search_pattern)) |
            (VoiceCallLog.call_sid.ilike(search_pattern))
        )

    calls = query.order_by(VoiceCallLog.created_at.desc()).limit(limit).all()

    total_calls = db.query(VoiceCallLog).count()
    recovered_calls = db.query(VoiceCallLog).filter(VoiceCallLog.call_status == "recovered").count()
    ptp_calls = db.query(VoiceCallLog).filter(VoiceCallLog.call_status == "ptp_committed").count()
    completed_calls = db.query(VoiceCallLog).filter(VoiceCallLog.call_status.in_(["completed", "recovered", "ptp_committed"])).count()
    unreachable_calls = db.query(VoiceCallLog).filter(VoiceCallLog.call_status == "failed_unreachable").count()
    pending_retry_calls = db.query(VoiceCallLog).filter(VoiceCallLog.call_status == "pending_retry").count()

    ptp_captured_value = db.query(func.sum(VoiceCallLog.captured_ptp_amount)).scalar() or 0.0

    return {
        "summary": {
            "total_calls_initiated": total_calls,
            "completed_calls": completed_calls,
            "recovered_calls": recovered_calls,
            "ptp_calls": ptp_calls,
            "unreachable_calls": unreachable_calls,
            "pending_retry_calls": pending_retry_calls,
            "call_completion_rate": round((completed_calls / max(total_calls, 1)) * 100, 1),
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
                "voice_persona": getattr(c, "voice_persona", None) or "priya",
                "transaction_id": getattr(c, "transaction_id", None),
                "duration_seconds": c.duration_seconds,
                "call_status": c.call_status,
                "transcript_hinglish": c.transcript_hinglish,
                "transcript_english": c.transcript_english,
                "detected_intent": c.detected_intent,
                "detected_objection": c.detected_objection,
                "captured_ptp_date": c.captured_ptp_date.isoformat() if c.captured_ptp_date else None,
                "captured_ptp_amount": c.captured_ptp_amount,
                "audio_simulation_url": c.audio_simulation_url or "/audio/voices/priya_payment_retry.mp3",
                "recording_url": c.audio_simulation_url or "/audio/voices/priya_payment_retry.mp3",
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in calls
        ]
    }


def generate_persona_script(persona: str, scenario: str, name: str, amt_str: str) -> tuple[str, str, str]:
    """Generates persona-specific Hinglish dialogue, English translation, and audio URL."""
    persona_key = persona.lower() if persona else "priya"
    if persona_key not in PERSONAS:
        persona_key = "priya"

    p_info = PERSONAS[persona_key]
    audio_filename = f"{persona_key}_{scenario}.mp3"
    audio_url = f"/audio/voices/{audio_filename}"

    if scenario == "salary_pending":
        if p_info["gender"] == "male":
            hinglish = (
                f"Namaste {name} ji! Main UrbanKart Accounts team se {p_info['name']} baat kar raha hoon. "
                f"Aapka {amt_str} ka payment bank decline ki wajah se pending tha. "
                f"Humein maloom hai ki salary cycle pending ho sakti hai. "
                f"Aapka Promise to Pay schedule karne ke liye kripya keypad par 2 dabayein, ya abhi pay karne ke liye 1 dabayein."
            )
            english = (
                f"Hello {name}! This is {p_info['name']} from UrbanKart Accounts team. "
                f"Your payment of {amt_str} was interrupted by bank decline. "
                f"We recognize your salary cycle may be pending. Press 2 to schedule a Promise-to-Pay, or Press 1 to pay now."
            )
        else:
            hinglish = (
                f"Namaste {name} ji! Main UrbanKart recovery desk se {p_info['name']} bol rahi hoon. "
                f"Aapka {amt_str} ka payment bank decline ki wajah se pending tha. "
                f"Kya aap ise abhi settle karna chahenge ya salary aane tak schedule karein? "
                f"Instant link ke liye 1 dabayein, ya agle teen din baad payment karne ke liye 2 dabayein."
            )
            english = (
                f"Hello {name}! This is {p_info['name']} from UrbanKart recovery desk. "
                f"Your payment of {amt_str} was pending due to bank decline. "
                f"Would you like to settle now or schedule after salary credit? Press 1 for instant link, or Press 2 to schedule."
            )

    elif scenario == "mandate_failure":
        if p_info["gender"] == "male":
            hinglish = (
                f"Namaste {name} ji! Main {p_info['name']} baat kar raha hoon. "
                f"Aapka monthly subscription recurring mandate auto-debit {amt_str} decline ho gaya hai. "
                f"Apni services uninterrupted continue rakhne ke liye kripya keypad par 1 dabayein aur apna payment complete karein."
            )
            english = (
                f"Hello {name}! This is {p_info['name']}. "
                f"Your monthly subscription auto-debit of {amt_str} failed. "
                f"To keep your services active without disruption, please press 1 on your keypad to settle via UPI."
            )
        else:
            hinglish = (
                f"Namaste {name} ji! Aapka monthly subscription auto-debit {amt_str} decline ho gaya hai. "
                f"Apni services uninterrupted continue rakhne ke liye kripya keypad par 1 dabayein aur payment turant complete karein."
            )
            english = (
                f"Hello {name}! Your monthly subscription debit of {amt_str} was declined. "
                f"To prevent any service interruption, please press 1 on your keypad to complete payment."
            )

    elif scenario == "failed_call":
        if p_info["gender"] == "male":
            hinglish = (
                f"Namaste {name} ji! Main UrbanKart Priority Recovery desk se {p_info['name']} baat kar raha hoon. "
                f"Aapka transaction {amt_str} bank network error ki wajah se fail hua tha, par aapke paise bilkul safe hain. "
                f"Turant 1-click WhatsApp payment link paane ke liye keypad par 1 dabayein, ya payment postpone karne ke liye 2 dabayein."
            )
            english = (
                f"Hello {name}! This is {p_info['name']} from UrbanKart Recovery desk. "
                f"Your transaction of {amt_str} failed due to bank network error, but your funds are safe. "
                f"Press 1 to receive a 1-click link on WhatsApp, or Press 2 to schedule later."
            )
        else:
            hinglish = (
                f"Namaste {name} ji! Main {p_info['name']} baat kar rahi hoon UrbanKart Priority desk se. "
                f"Aapka {amt_str} ka transaction gateway error ki wajah se fail ho gaya tha. "
                f"Humne aapka order safe hold par rakha hai. Instant 1-click retry ke liye keypad par 1 dabayein."
            )
            english = (
                f"Hello {name}! This is {p_info['name']} from UrbanKart. "
                f"Your transaction of {amt_str} failed due to a gateway error. "
                f"Your order is held safely. Press 1 on your keypad for instant 1-click retry."
            )

    elif scenario == "pending_call":
        if p_info["gender"] == "male":
            hinglish = (
                f"Namaste {name} ji! {p_info['name']} yahan UrbanKart desk se. "
                f"Aapka order payment {amt_str} bank verification stage par pending hai. "
                f"Ise double-charge se bachate hue complete karne ke liye keypad par 1 dabayein."
            )
            english = (
                f"Hello {name}! This is {p_info['name']} from UrbanKart. "
                f"Your payment of {amt_str} is currently pending bank authorization. "
                f"Press 1 to complete the transaction safely without double deduction."
            )
        else:
            hinglish = (
                f"Namaste {name} ji! Main {p_info['name']} baat kar rahi hoon. "
                f"Aapka payment {amt_str} authorization pending stage par hai. "
                f"Ise safely 1-click UPI se complete karne ke liye keypad par 1 dabayein."
            )
            english = (
                f"Hello {name}! This is {p_info['name']}. "
                f"Your payment of {amt_str} is pending bank authorization. "
                f"Press 1 to confirm and complete via 1-click UPI."
            )

    else:  # payment_retry
        if p_info["gender"] == "male":
            hinglish = (
                f"Namaste {name} ji! Main UrbanKart Accounts team se {p_info['name']} baat kar raha hoon. "
                f"Aapka pending transaction {amt_str} instant retry ke liye ready hai. "
                f"Instant UPI link ke liye keypad par 1 dabayein, ya payment schedule karne ke liye 2 dabayein."
            )
            english = (
                f"Hello {name}! This is {p_info['name']} from UrbanKart Accounts team. "
                f"Your transaction of {amt_str} is ready for instant retry. Press 1 for a WhatsApp link or Press 2 to reschedule."
            )
        else:
            hinglish = (
                f"Namaste {name} ji! Main UrbanKart Priority Care desk se {p_info['name']} baat kar rahi hoon. "
                f"Aapka {amt_str} ka recent payment bank connectivity timeout ki wajah se hold pe tha. "
                f"Aap ise 1-click UPI ke through turant bina kisi delay ke complete kar sakte hain. "
                f"WhatsApp par instant payment link paane ke liye kripya keypad par 1 dabayein, ya payment schedule karne ke liye 2 dabayein."
            )
            english = (
                f"Hello {name}! This is {p_info['name']} from UrbanKart Priority Care. "
                f"Your recent order payment of {amt_str} timed out at the bank. "
                f"Press 1 on your keypad to receive an instant UPI payment link on WhatsApp, or Press 2 to schedule payment."
            )

    return hinglish, english, audio_url


@router.post("/voice/call/dispatch")
def dispatch_voice_call(
    payload: VoiceCallDispatchRequest,
    db: Session = Depends(get_db)
):
    """
    Free Outbound Voice Calling API with Multi-Voice Support & Call Recording.
    Initiates AI outbound phone call via free WebRTC Softphone Gateway or Telecom Sandbox.
    """
    call_sid = f"CA_free_{uuid.uuid4().hex[:14]}"
    merchant = db.query(Merchant).first()
    customer = db.query(Customer).filter(Customer.phone == payload.phone_number).first() or db.query(Customer).first()

    amt_formatted = f"Rs.{payload.amount:,.2f}" if payload.amount else "Rs.14,500"
    voice_persona = (payload.voice_persona or "priya").lower()
    if voice_persona not in PERSONAS:
        voice_persona = "priya"

    scenario = payload.scenario or "payment_retry"

    if payload.custom_script:
        dialogue_hinglish = payload.custom_script
        dialogue_english = payload.custom_script
        audio_url = f"/audio/voices/{voice_persona}_payment_retry.mp3"
    else:
        dialogue_hinglish, dialogue_english, audio_url = generate_persona_script(
            persona=voice_persona,
            scenario=scenario,
            name=payload.customer_name or "Valued Customer",
            amt_str=amt_formatted
        )

    # Persist in VoiceCallLog with recording URL and persona
    call_log = VoiceCallLog(
        id=str(uuid.uuid4()),
        merchant_id=merchant.id if merchant else "merchant_urbankart",
        customer_id=customer.id if customer else None,
        customer_name=payload.customer_name or "Valued Customer",
        customer_phone=payload.phone_number,
        call_sid=call_sid,
        language=payload.language or "hinglish",
        voice_persona=voice_persona,
        transaction_id=payload.transaction_id,
        duration_seconds=46,
        call_status="in_progress",
        transcript_hinglish=dialogue_hinglish,
        transcript_english=dialogue_english,
        detected_intent=f"Outbound AI recovery conversation initialized via {voice_persona.upper()}",
        detected_objection=scenario,
        captured_ptp_date=datetime.utcnow() + timedelta(days=2),
        captured_ptp_amount=payload.amount,
        audio_simulation_url=audio_url
    )
    db.add(call_log)
    db.commit()

    return {
        "success": True,
        "call_id": call_log.id,
        "call_sid": call_sid,
        "status": "in-progress",
        "provider": "Free In-Browser WebRTC & Telephony Gateway",
        "cost": "Rs. 0.00 (100% Free Demo API)",
        "voice_persona": voice_persona,
        "persona_details": PERSONAS[voice_persona],
        "scenario": scenario,
        "transaction_id": payload.transaction_id,
        "recipient_phone": payload.phone_number,
        "customer_name": payload.customer_name,
        "amount": payload.amount,
        "transcript_hinglish": dialogue_hinglish,
        "transcript_english": dialogue_english,
        "audio_url": audio_url,
        "recording_url": audio_url,
        "dtmf_menu": {
            "1": "Send 1-Click WhatsApp payment link",
            "2": "Record Promise-to-Pay (PTP) for scheduled date",
            "3": "Connect to senior operations desk"
        },
        "created_at": datetime.utcnow().isoformat()
    }


@router.post("/voice/call/dtmf")
def handle_call_dtmf(
    payload: DTMFPayload,
    db: Session = Depends(get_db)
):
    """
    Handles in-call DTMF Keypad presses:
    Key 1: Send instant payment link -> Marks call as RECOVERED with voice ack
    Key 2: Schedule Promise-to-Pay -> Marks call as PTP_COMMITTED with voice ack
    Key 3: Transfer to human escalation desk
    """
    merchant = db.query(Merchant).first()
    ptp_target_date = datetime.utcnow() + timedelta(days=3)

    # Find active call record
    call = db.query(VoiceCallLog).filter(VoiceCallLog.call_sid == payload.call_sid).first()
    persona = getattr(call, "voice_persona", None) or payload.voice_persona or "priya"
    is_male = persona in ["rahul", "madhur"]

    ack_audio_url = None
    if payload.digit == "1":
        action = "whatsapp_payment_link_dispatched"
        message = "1-Click UPI Payment link sent to customer's WhatsApp & SMS."
        ack_audio_url = f"/audio/voices/dtmf_key1_ack_{'male' if is_male else 'female'}.mp3"

        if call:
            call.call_status = "recovered"
            call.detected_intent = "Customer accepted 1-Click WhatsApp payment link"
            if call.transaction_id:
                tx = db.query(Transaction).filter(Transaction.id == call.transaction_id).first()
                if tx:
                    tx.status = TransactionStatus.SUCCESS
            db.commit()

    elif payload.digit == "2":
        action = "ptp_commitment_logged"
        message = f"Promise-to-Pay confirmed for {ptp_target_date.strftime('%A, %d %b')}."
        ack_audio_url = f"/audio/voices/dtmf_key2_ack_{'male' if is_male else 'female'}.mp3"

        if call:
            call.call_status = "ptp_committed"
            call.detected_intent = f"PTP scheduled for {ptp_target_date.strftime('%Y-%m-%d')}"
            call.captured_ptp_date = ptp_target_date
            call.captured_ptp_amount = payload.amount or 14500.0

        ptp = PromiseToPay(
            id=str(uuid.uuid4()),
            merchant_id=merchant.id if merchant else "merchant_urbankart",
            customer_id=call.customer_id if call and call.customer_id else str(uuid.uuid4()),
            customer_name=payload.customer_name or "Valued Customer",
            reference_type="voice_call",
            reference_id=payload.call_sid,
            promised_amount=payload.amount or 14500.0,
            promised_date=ptp_target_date,
            channel_source="voice_agent",
            fulfillment_status="pending",
            reliability_score=88.5
        )
        db.add(ptp)
        db.commit()
    else:
        action = "agent_escalation"
        message = "Transferred to Priority Fintech Escalation Desk."
        if call:
            call.call_status = "escalated"
            call.detected_intent = "Customer requested live supervisor escalation"
            db.commit()

    return {
        "success": True,
        "call_sid": payload.call_sid,
        "digit_pressed": payload.digit,
        "action": action,
        "message": message,
        "call_status": call.call_status if call else "completed",
        "ack_audio_url": ack_audio_url
    }


@router.post("/voice/call/update-status")
def update_call_status(
    payload: CallStatusUpdateRequest,
    db: Session = Depends(get_db)
):
    """Updates call record status (e.g. hung up, completed, unreachable) preserving recovery states."""
    call = db.query(VoiceCallLog).filter(VoiceCallLog.call_sid == payload.call_sid).first()
    if not call:
        return {"success": False, "error": "Call not found"}

    # Preserve positive recovery or PTP status if already achieved
    if call.call_status in ["recovered", "ptp_committed"]:
        if payload.call_status not in ["recovered", "ptp_committed"]:
            pass  # keep current positive status
        else:
            call.call_status = payload.call_status
    else:
        call.call_status = payload.call_status or "completed"

    if payload.duration_seconds is not None:
        call.duration_seconds = max(1, payload.duration_seconds)

    db.commit()
    return {
        "success": True,
        "call_sid": payload.call_sid,
        "call_status": call.call_status,
        "duration_seconds": call.duration_seconds,
        "recording_url": call.audio_simulation_url,
        "message": f"Call status updated to {call.call_status} and recording synced."
    }


class SaveRecordingRequest(BaseModel):
    call_sid: str
    customer_name: Optional[str] = "Valued Customer"
    customer_phone: Optional[str] = None
    amount: Optional[float] = 14500.0
    duration_seconds: Optional[int] = 45
    call_status: Optional[str] = "completed"
    voice_persona: Optional[str] = "priya"
    scenario: Optional[str] = "payment_retry"
    recording_url: Optional[str] = None
    transaction_id: Optional[str] = None
    transcript_hinglish: Optional[str] = None
    transcript_english: Optional[str] = None


@router.post("/voice/call/save-recording")
def save_call_recording(
    payload: SaveRecordingRequest,
    db: Session = Depends(get_db)
):
    """
    Explicitly saves or updates a call recording in the VoiceCallLog ledger.
    Guarantees that every completed call is recorded and appears in Call History.
    """
    call = db.query(VoiceCallLog).filter(VoiceCallLog.call_sid == payload.call_sid).first()

    persona = (payload.voice_persona or "priya").lower()
    scenario = payload.scenario or "payment_retry"
    recording_url = payload.recording_url or f"/audio/voices/{persona}_{scenario}.mp3"

    if call:
        call.audio_simulation_url = recording_url
        if payload.call_status:
            # Preserve recovered or ptp if already registered
            if call.call_status not in ["recovered", "ptp_committed"] or payload.call_status in ["recovered", "ptp_committed"]:
                call.call_status = payload.call_status
        if payload.duration_seconds is not None:
            call.duration_seconds = max(1, payload.duration_seconds)
        if payload.voice_persona:
            call.voice_persona = payload.voice_persona
        if payload.transaction_id:
            call.transaction_id = payload.transaction_id
    else:
        merchant = db.query(Merchant).first()
        customer = db.query(Customer).filter(Customer.phone == payload.customer_phone).first() if payload.customer_phone else None

        amt_str = f"Rs.{payload.amount:,.2f}" if payload.amount else "Rs.14,500"
        h_script, e_script, _ = generate_persona_script(
            persona=persona,
            scenario=scenario,
            name=payload.customer_name or "Valued Customer",
            amt_str=amt_str
        )

        call = VoiceCallLog(
            id=str(uuid.uuid4()),
            merchant_id=merchant.id if merchant else "merchant_urbankart",
            customer_id=customer.id if customer else None,
            customer_name=payload.customer_name or "Valued Customer",
            customer_phone=payload.customer_phone or "+91 9876543210",
            call_sid=payload.call_sid,
            language="hinglish",
            voice_persona=persona,
            transaction_id=payload.transaction_id,
            duration_seconds=max(1, payload.duration_seconds or 45),
            call_status=payload.call_status or "completed",
            transcript_hinglish=payload.transcript_hinglish or h_script,
            transcript_english=payload.transcript_english or e_script,
            detected_intent="Outbound recovery conversation recorded",
            detected_objection=scenario,
            captured_ptp_date=datetime.utcnow() + timedelta(days=3) if payload.call_status == "ptp_committed" else None,
            captured_ptp_amount=payload.amount,
            audio_simulation_url=recording_url
        )
        db.add(call)

    db.commit()

    return {
        "success": True,
        "call_sid": payload.call_sid,
        "recording_url": call.audio_simulation_url,
        "call_status": call.call_status,
        "duration_seconds": call.duration_seconds,
        "voice_persona": call.voice_persona,
        "message": "Call recording and metadata successfully saved to database ledger."
    }


@router.post("/voice/call/upload-recording")
async def upload_call_recording(
    call_sid: str = Form(...),
    duration_seconds: Optional[int] = Form(None),
    call_status: Optional[str] = Form("completed"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Accepts raw audio recorded in-browser (Blob / WebM / MP3) and saves to audio vault.
    Updates the call record with the saved recording URL.
    """
    recordings_dir = os.path.join(PROJECT_ROOT, "frontend", "public", "audio", "recordings")
    os.makedirs(recordings_dir, exist_ok=True)

    clean_sid = call_sid.replace("/", "_").replace("\\", "_").replace(" ", "_")
    filename = f"rec_{clean_sid}.webm"
    filepath = os.path.join(recordings_dir, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    recording_url = f"/audio/recordings/{filename}"

    call = db.query(VoiceCallLog).filter(VoiceCallLog.call_sid == call_sid).first()
    if call:
        call.audio_simulation_url = recording_url
        if call_status:
            call.call_status = call_status
        if duration_seconds is not None:
            call.duration_seconds = max(1, duration_seconds)
        db.commit()

    return {
        "success": True,
        "call_sid": call_sid,
        "recording_url": recording_url,
        "bytes_saved": len(content),
        "call_status": call.call_status if call else call_status,
        "duration_seconds": call.duration_seconds if call else duration_seconds,
        "message": "Audio call recording successfully saved to disk and database ledger."
    }

