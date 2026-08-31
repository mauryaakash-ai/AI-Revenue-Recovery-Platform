"""
Automated Pytest Suite for Enterprise Revenue Recovery Modules:
1. Checkout Drop-off Recovery
2. Subscription Dunning & Involuntary Churn
3. B2B Receivables Chaser
4. Mandate Retry Sequencer
5. Hinglish Voice Recovery
6. Promise-to-Pay (PTP) Tracker
7. Stopping Rules & Compliance Guardrails
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import uuid

from app.main import app
from app.database import SessionLocal
from app.models import (
    Merchant, Customer, CheckoutDropoff, SubscriptionDunning,
    B2BInvoice, MandateRetry, VoiceCallLog, PromiseToPay, ComplianceRuleLog
)

client = TestClient(app)


def test_checkout_dropoff_list_and_nudge():
    """Test checkout drop-off query and resume nudge dispatch"""
    res = client.get("/api/v1/checkout-dropoff/list")
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert "items" in data
    assert data["summary"]["total_abandoned_sessions"] >= 0

    if data["items"]:
        first_id = data["items"][0]["id"]
        # Dispatch nudge
        nudge_res = client.post(f"/api/v1/checkout-dropoff/{first_id}/nudge", json={
            "channel": "whatsapp",
            "discount_code": "SAVE10"
        })
        assert nudge_res.status_code == 200
        assert nudge_res.json()["success"] is True

        # Simulate conversion
        conv_res = client.post(f"/api/v1/checkout-dropoff/{first_id}/simulate-conversion")
        assert conv_res.status_code == 200
        assert conv_res.json()["success"] is True


def test_subscription_dunning_and_action():
    """Test subscription dunning query and smart retry execution"""
    res = client.get("/api/v1/dunning/subscriptions")
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert "items" in data

    if data["items"]:
        first_id = data["items"][0]["id"]
        action_res = client.post(f"/api/v1/dunning/{first_id}/action", json={
            "action": "retry_now"
        })
        assert action_res.status_code == 200
        assert action_res.json()["status"] == "recovered"


def test_b2b_chaser_and_settlement():
    """Test B2B receivables aging buckets, reminder dispatch, and settlement"""
    res = client.get("/api/v1/b2b-chaser/invoices")
    assert res.status_code == 200
    data = res.json()
    assert "aging_buckets" in data["summary"]

    if data["items"]:
        first_id = data["items"][0]["id"]
        # Send reminder
        rem_res = client.post(f"/api/v1/b2b-chaser/{first_id}/send-reminder", json={
            "stage": "formal_notice",
            "channel": "email"
        })
        assert rem_res.status_code == 200
        assert rem_res.json()["success"] is True

        # Settle invoice
        settle_res = client.post(f"/api/v1/b2b-chaser/{first_id}/settle")
        assert settle_res.status_code == 200
        assert settle_res.json()["success"] is True


def test_mandate_retry_sequencer():
    """Test mandate retry queue and RBI compliant sequence execution"""
    res = client.get("/api/v1/mandates/queue")
    assert res.status_code == 200
    data = res.json()
    assert "attempt_distribution" in data["summary"]

    if data["items"]:
        first_id = data["items"][0]["id"]
        act_res = client.post(f"/api/v1/mandates/{first_id}/action", json={
            "action": "sequence_retry_now"
        })
        assert act_res.status_code == 200
        assert act_res.json()["success"] is True


def test_hinglish_voice_call_simulation():
    """Test outbound Hinglish AI voice simulation and PTP capture"""
    sim_res = client.post("/api/v1/voice/simulate-call", json={
        "customer_name": "Akash Test",
        "customer_phone": "+91 9820194821",
        "amount": 12500.0,
        "customer_objection": "salary_pending"
    })
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert sim_data["success"] is True
    assert "Namaste" in sim_data["transcript_hinglish"]
    assert sim_data["captured_ptp_date"] is not None


def test_promise_to_pay_lifecycle():
    """Test PTP record creation, retrieval, and fulfillment score adjustments"""
    # Create PTP
    create_res = client.post("/api/v1/ptp/create", json={
        "customer_name": "Rohan Verma",
        "reference_type": "transaction",
        "reference_id": "TXN_TEST_99",
        "promised_amount": 25000.0,
        "promised_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
        "channel_source": "voice_agent"
    })
    assert create_res.status_code == 200
    ptp_id = create_res.json()["ptp_id"]

    # Mark Kept
    kept_res = client.post(f"/api/v1/ptp/{ptp_id}/update-status", json={
        "fulfillment_status": "kept"
    })
    assert kept_res.status_code == 200
    assert kept_res.json()["fulfillment_status"] == "kept"
    assert kept_res.json()["updated_reliability_score"] >= 85.0


def test_compliance_guardrails_preflight():
    """Test pre-flight compliance blocking on quiet hours, DND, and max retries"""
    # 1. Blocked because already recovered
    chk1 = client.post("/api/v1/guardrails/check", json={
        "target_type": "transaction",
        "target_id": "TXN_101",
        "channel": "whatsapp",
        "attempt_count_today": 1,
        "is_already_recovered": True
    })
    assert chk1.status_code == 200
    assert chk1.json()["is_allowed"] is False
    assert chk1.json()["action_taken"] == "halted_recovered"

    # 2. Blocked because DND registered
    chk2 = client.post("/api/v1/guardrails/check", json={
        "customer_phone": "+91 9820192831",
        "target_type": "transaction",
        "target_id": "TXN_102",
        "channel": "voice_call",
        "attempt_count_today": 1,
        "is_dnd_registered": True
    })
    assert chk2.status_code == 200
    assert chk2.json()["is_allowed"] is False
    assert chk2.json()["action_taken"] == "blocked_dnd"

    # 3. Blocked because max attempts reached
    chk3 = client.post("/api/v1/guardrails/check", json={
        "target_type": "transaction",
        "target_id": "TXN_103",
        "channel": "card_retry",
        "attempt_count_today": 3
    })
    assert chk3.status_code == 200
    assert chk3.json()["is_allowed"] is False
    assert chk3.json()["action_taken"] == "throttled_max_attempts"

    # 4. Allowed clean dispatch
    chk4 = client.post("/api/v1/guardrails/check", json={
        "target_type": "transaction",
        "target_id": "TXN_104",
        "channel": "whatsapp",
        "attempt_count_today": 1
    })
    assert chk4.status_code == 200
    assert chk4.json()["is_allowed"] is True
    assert chk4.json()["action_taken"] == "dispatched"

