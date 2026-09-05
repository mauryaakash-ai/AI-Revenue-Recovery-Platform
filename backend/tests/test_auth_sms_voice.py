"""
Automated Pytest Suite for New Features:
1. Free Demo SMS API (templates, send, logs, demo-trigger)
2. Authentication & Login API (email, demo personas, SMS OTP dispatch and verification)
3. Free Outbound Voice Calling API (dispatch, DTMF interaction)
"""

try:
    import pytest
except ImportError:
    pytest = None
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import uuid

from app.main import app
from app.database import SessionLocal
from app.models import Merchant, Customer, SMSLog, User, VoiceCallLog, PromiseToPay

client = TestClient(app)


def test_sms_templates():
    """Verify pre-approved TRAI DLT templates are available"""
    res = client.get("/api/v1/sms/templates")
    assert res.status_code == 200
    data = res.json()
    assert "templates" in data
    assert len(data["templates"]) >= 5
    template_ids = [t["id"] for t in data["templates"]]
    assert "cart_recovery" in template_ids
    assert "payment_retry" in template_ids
    assert "login_otp" in template_ids


def test_sms_send_and_logs():
    """Verify sending a demo SMS and checking delivery log ledger"""
    res = client.post("/api/v1/sms/send", json={
        "recipient_phone": "+91 98201 94821",
        "template_name": "payment_retry",
        "template_params": {
            "amount": "14,634.05",
            "link": "https://rzp.io/l/test01"
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "details" in data
    assert data["details"]["status"] == "delivered"
    assert data["details"]["cost_inr"] == 0.0

    # Retrieve logs
    logs_res = client.get("/api/v1/sms/logs")
    assert logs_res.status_code == 200
    logs_data = logs_res.json()
    assert "summary" in logs_data
    assert "items" in logs_data
    assert logs_data["summary"]["total_dispatched"] >= 1
    assert logs_data["summary"]["free_demo_cost"] == "Rs. 0.00"


def test_sms_demo_trigger():
    """Verify 1-click test scenario dispatch"""
    res = client.post("/api/v1/sms/demo-trigger", json={
        "scenario": "cart_recovery",
        "recipient_phone": "+91 98201 94821",
        "customer_name": "Akash Sharma",
        "amount": 14500.0
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["scenario"] == "cart_recovery"
    assert "SAVE10" in data["dispatch"]["message_body"]


def test_auth_personas_and_login():
    """Verify demo personas endpoint and 1-click login"""
    res = client.get("/api/v1/auth/personas")
    assert res.status_code == 200
    data = res.json()
    assert "personas" in data
    assert len(data["personas"]) == 4

    # Login with persona Akash Sharma
    login_res = client.post("/api/v1/auth/login", json={
        "email": "akash@urbankart.com",
        "persona_id": "usr_akash_01"
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["success"] is True
    assert login_data["user"]["name"] == "Akash Sharma"
    assert login_data["user"]["role"] == "Admin"
    assert "tok_" in login_data["token"]


def test_auth_sms_otp_flow():
    """Verify requesting and verifying OTP via the new Demo SMS API"""
    # 1. Send OTP
    send_res = client.post("/api/v1/auth/send-otp", json={
        "phone": "+91 98201 94821"
    })
    assert send_res.status_code == 200
    send_data = send_res.json()
    assert send_data["success"] is True
    otp_code = send_data["demo_otp_hint"]
    assert len(otp_code) == 6

    # 2. Verify with invalid OTP
    bad_res = client.post("/api/v1/auth/verify-otp", json={
        "phone": "+91 98201 94821",
        "otp": "000000"
    })
    assert bad_res.status_code == 400

    # 3. Verify with valid OTP
    good_res = client.post("/api/v1/auth/verify-otp", json={
        "phone": "+91 98201 94821",
        "otp": otp_code
    })
    assert good_res.status_code == 200
    good_data = good_res.json()
    assert good_data["success"] is True
    assert "token" in good_data
    assert good_data["user"]["name"] == "Akash Sharma"


def test_free_voice_call_dispatch_and_dtmf():
    """Verify free outbound voice call dispatch and DTMF key processing"""
    # Dispatch call
    call_res = client.post("/api/v1/voice/call/dispatch", json={
        "phone_number": "+91 98201 94821",
        "customer_name": "Akash Sharma",
        "amount": 14500.0,
        "scenario": "salary_pending"
    })
    assert call_res.status_code == 200
    call_data = call_res.json()
    assert call_data["success"] is True
    assert "CA_free_" in call_data["call_sid"]
    assert call_data["status"] == "in-progress"
    assert "Rs. 0.00" in call_data["cost"]

    call_sid = call_data["call_sid"]

    # Press DTMF 1 (WhatsApp Payment Link)
    dtmf1 = client.post("/api/v1/voice/call/dtmf", json={
        "call_sid": call_sid,
        "digit": "1",
        "customer_phone": "+91 98201 94821",
        "amount": 14500.0
    })
    assert dtmf1.status_code == 200
    assert dtmf1.json()["action"] == "whatsapp_payment_link_dispatched"

    # Press DTMF 2 (PTP Confirmation)
    dtmf2 = client.post("/api/v1/voice/call/dtmf", json={
        "call_sid": call_sid,
        "digit": "2",
        "customer_phone": "+91 98201 94821",
        "customer_name": "Akash Sharma",
        "amount": 14500.0
    })
    assert dtmf2.status_code == 200
    assert dtmf2.json()["action"] == "ptp_commitment_logged"
    assert "ack_audio_url" in dtmf2.json()


def test_voice_personas_and_multi_voice_dispatch():
    """Verify 5 studio neural voice personas and persona-specific audio dispatch"""
    res = client.get("/api/v1/voice/personas")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] == 5
    persona_ids = [p["id"] for p in data["personas"]]
    assert "priya" in persona_ids
    assert "rahul" in persona_ids
    assert "swara" in persona_ids
    assert "madhur" in persona_ids
    assert "kavya" in persona_ids

    # Test dispatching with Rahul
    call_rahul = client.post("/api/v1/voice/call/dispatch", json={
        "phone_number": "+91 98469 13810",
        "customer_name": "Ananya Sharma",
        "amount": 45000.0,
        "scenario": "failed_call",
        "voice_persona": "rahul"
    })
    assert call_rahul.status_code == 200
    rahul_data = call_rahul.json()
    assert rahul_data["voice_persona"] == "rahul"
    assert "/audio/voices/rahul_failed_call.mp3" in rahul_data["audio_url"]
    assert "Rahul" in rahul_data["transcript_hinglish"]

    # Test dispatching with Swara
    call_swara = client.post("/api/v1/voice/call/dispatch", json={
        "phone_number": "+91 98366 87537",
        "customer_name": "Aarav Sen",
        "amount": 12400.0,
        "scenario": "pending_call",
        "voice_persona": "swara"
    })
    assert call_swara.status_code == 200
    swara_data = call_swara.json()
    assert swara_data["voice_persona"] == "swara"
    assert "/audio/voices/swara_pending_call.mp3" in swara_data["audio_url"]


def test_voice_calling_queue_pending_and_failed():
    """Verify outbound calling queue filters and categorizes pending and failed calls"""
    # Fetch queue
    res = client.get("/api/v1/voice/calling-queue?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert "items" in data
    assert data["summary"]["failed_transactions_count"] > 0
    assert data["summary"]["pending_transactions_count"] > 0
    assert data["summary"]["total_at_risk_amount"] > 0

    first_item = data["items"][0]
    assert "transaction_id" in first_item
    assert "customer_name" in first_item
    assert "amount" in first_item
    assert first_item["transaction_status"] in ["FAILED", "PENDING"]
    assert first_item["recommended_persona"] in ["priya", "rahul", "swara", "madhur", "kavya"]
    assert first_item["recommended_scenario"] in ["failed_call", "pending_call", "payment_retry", "salary_pending", "mandate_failure"]


def test_call_recordings_in_history():
    """Verify every call history item contains audio recording URL and persona"""
    res = client.get("/api/v1/voice/calls?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert len(data["items"]) > 0

    for call in data["items"]:
        assert "recording_url" in call
        assert call["recording_url"] is not None
        assert call["recording_url"].endswith(".mp3")
        assert "voice_persona" in call
        assert call["voice_persona"] in ["priya", "rahul", "swara", "madhur", "kavya"]


