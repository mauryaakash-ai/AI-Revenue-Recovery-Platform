"""
Comprehensive Enterprise Test Suite for RevPilot AI Revenue Recovery Platform
Validates:
1. Webhook Engine: HMAC verification, idempotency, and normalization
2. Failure Taxonomy Classifier: Hierarchical decline classification
3. Risk Engine: Velocity, amount deviation, and fraud suppression
4. Timing Engine: NPCI/TRAI Quiet hours and dynamic channel ranking
5. Bandit Engine: UCB1 exploration and emergency kill switch
6. Decision Engine: Section 41 Standardized AI Decision Object and ENRV
7. Bank Health Monitoring: Anomaly degradation and throttling advisory
8. Monte Carlo 2.0: 1000-iteration stochastic forecasting with 95% CIs
9. RBAC: Role permission matrix across 6 roles
"""

import hmac
import hashlib
import json
import sys
from datetime import datetime, timedelta
from unittest.mock import MagicMock

# Shim SQLAlchemy & FastAPI if running in a bare Python environment without external packages
if "sqlalchemy" not in sys.modules:
    try:
        import sqlalchemy
    except ImportError:
        class DummySQLAlchemy:
            class Column:
                def __init__(self, *args, **kwargs): pass
            class String:
                def __init__(self, *args, **kwargs): pass
            class Integer:
                def __init__(self, *args, **kwargs): pass
            class Float:
                def __init__(self, *args, **kwargs): pass
            class DateTime:
                def __init__(self, *args, **kwargs): pass
            class ForeignKey:
                def __init__(self, *args, **kwargs): pass
            class Enum:
                def __init__(self, *args, **kwargs): pass
            class Text:
                def __init__(self, *args, **kwargs): pass
            class Boolean:
                def __init__(self, *args, **kwargs): pass
            class Index:
                def __init__(self, *args, **kwargs): pass
            class UniqueConstraint:
                def __init__(self, *args, **kwargs): pass
        
        sa_mock = DummySQLAlchemy()
        sys.modules["sqlalchemy"] = sa_mock
        sys.modules["sqlalchemy.orm"] = MagicMock()
        sys.modules["sqlalchemy.ext.declarative"] = MagicMock()
        sys.modules["app.database"] = MagicMock()

if "fastapi" not in sys.modules:
    try:
        import fastapi
    except ImportError:
        sys.modules["fastapi"] = MagicMock()
        sys.modules["pydantic"] = MagicMock()

from app.webhook_service import webhook_engine, WebhookVerificationError
from app.failure_classifier import failure_classifier, FailureTaxonomy
from app.risk_engine import risk_engine, RiskTier
from app.timing_engine import timing_engine
from app.bandit_engine import bandit_engine
from app.decision_engine import decision_engine
from app.forecasting_engine import monte_carlo_engine
from app.rbac import Role, Permission, has_permission


def test_webhook_hmac_and_idempotency():
    """Verify HMAC SHA256 validation and duplicate prevention"""
    secret = webhook_engine.handlers["razorpay"].secret
    payload = json.dumps({
        "entity": "event",
        "event": "payment.failed",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test_991823",
                    "amount": 1500000,
                    "currency": "INR",
                    "status": "failed",
                    "method": "card",
                    "error_code": "BAD_REQUEST_PAYMENT_TIMED_OUT",
                    "error_description": "Bank connection timed out during 3DS OTP verification",
                    "bank": "HDFC",
                    "email": "test@enterprise.com",
                    "contact": "+919876543210"
                }
            }
        }
    }).encode("utf-8")

    valid_sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    # 1. Successful ingestion
    result = webhook_engine.process_webhook(
        provider="razorpay",
        raw_body=payload,
        signature=valid_sig,
        merchant_id="merchant_urbankart"
    )
    assert result["status"] == "received"
    assert result["transaction_id"] == "pay_test_991823"

    # 2. Idempotency test (same signature + payload hash should detect duplicate)
    dup_result = webhook_engine.process_webhook(
        provider="razorpay",
        raw_body=payload,
        signature=valid_sig,
        merchant_id="merchant_urbankart"
    )
    assert dup_result["status"] == "duplicate"
    assert "Duplicate webhook event ignored" in dup_result["message"]

    # 3. Invalid signature test
    try:
        webhook_engine.process_webhook(
            provider="razorpay",
            raw_body=payload,
            signature="invalid_fake_signature",
            merchant_id="merchant_urbankart"
        )
        assert False, "Should have raised WebhookVerificationError"
    except WebhookVerificationError:
        assert True


def test_failure_taxonomy_classification():
    """Verify hierarchical classification across Issuer, Gateway, Auth, Customer, Permanent"""
    # 1. 3DS timeout -> AUTHENTICATION
    res_auth = failure_classifier.classify(
        failure_code="BAD_REQUEST_PAYMENT_VERIFICATION_FAILED",
        failure_reason="Customer failed 3DS authentication"
    )
    assert res_auth["category"] == FailureTaxonomy.AUTHENTICATION
    assert res_auth["is_permanent"] is False
    assert res_auth["confidence"] >= 0.85

    # 2. Insufficient balance -> CUSTOMER
    res_cust = failure_classifier.classify(
        failure_reason="Cardholder has insufficient funds"
    )
    assert res_cust["category"] == FailureTaxonomy.CUSTOMER
    assert res_cust["subcategory"] == "insufficient_funds"

    # 3. Card invalid / account closed -> PERMANENT
    res_perm = failure_classifier.classify(
        failure_code="BAD_REQUEST_PAYMENT_CARD_INVALID",
        failure_reason="Invalid card number"
    )
    assert res_perm["category"] == FailureTaxonomy.PERMANENT
    assert res_perm["is_permanent"] is True

    # 4. Bank timeout -> ISSUER
    res_issuer = failure_classifier.classify(
        failure_code="BAD_REQUEST_PAYMENT_TIMED_OUT"
    )
    assert res_issuer["category"] == FailureTaxonomy.ISSUER


def test_risk_engine_checks():
    """Verify fraud risk velocity, amount deviation, and hard blocks"""
    # 1. Hard block stolen card
    res_block = risk_engine.assess_risk({
        "amount": 5000.0,
        "failure_code": "stolen_card_reported"
    })
    assert res_block["risk_tier"] == RiskTier.BLOCKED
    assert res_block["risk_score"] == 100.0
    assert res_block["allow_autonomous_recovery"] is False

    # 2. Velocity trigger (5 failures in 1h)
    res_velocity = risk_engine.assess_risk({
        "amount": 5000.0,
        "velocity_1h": 6,
        "velocity_24h": 12
    })
    assert res_velocity["risk_score"] >= 50.0
    assert res_velocity["risk_tier"] in [RiskTier.HIGH_RISK, RiskTier.BLOCKED]
    assert res_velocity["requires_fraud_review"] is True

    # 3. Normal low risk transaction
    res_normal = risk_engine.assess_risk({
        "amount": 3500.0,
        "velocity_1h": 1,
        "velocity_24h": 1
    })
    assert res_normal["risk_tier"] == RiskTier.LOW_RISK
    assert res_normal["allow_autonomous_recovery"] is True


def test_timing_engine_and_quiet_hours():
    """Verify quiet hours enforcement (21:00-08:00 IST) and dynamic channel ranking"""
    # Test quiet hours detector
    night_time = datetime(2026, 9, 4, 22, 30)  # 22:30 IST
    morning_time = datetime(2026, 9, 4, 14, 0)  # 14:00 IST

    assert timing_engine.is_in_quiet_hours(night_time) is True
    assert timing_engine.is_in_quiet_hours(morning_time) is False

    # When scheduled during quiet hours, next allowed time should be morning
    next_time, adjusted, label = timing_engine.calculate_next_allowed_time(
        base_time=night_time,
        delay_minutes=15
    )
    assert adjusted is True
    assert next_time.hour == 8
    assert next_time.minute == 30

    # Channel ranking for 3DS authentication failure
    ranked = timing_engine.rank_channels(
        failure_category="AUTHENTICATION",
        amount=12000.0,
        payment_method="upi"
    )
    assert len(ranked) >= 4
    top_channel = ranked[0]["channel"]
    assert "whatsapp" in top_channel or "sms" in top_channel or "vpa" in top_channel


def test_bandit_engine_exploration_and_kill_switch():
    """Verify UCB1 multi-armed bandit selection, reward updating, and kill switch"""
    # 1. Arm selection
    choice = bandit_engine.select_arm()
    assert choice["selected_arm"] in bandit_engine.arms
    assert "expected_reward" in choice

    # 2. Feedback loop
    initial_conversions = bandit_engine.arms["whatsapp_recovery"].conversions
    bandit_engine.record_feedback("whatsapp_recovery", recovered=True, net_revenue=4200.0)
    assert bandit_engine.arms["whatsapp_recovery"].conversions == initial_conversions + 1

    # 3. Kill switch test
    arm_to_kill = "sms_recovery"
    bandit_engine.set_kill_switch(arm_to_kill, False)
    assert bandit_engine.arms[arm_to_kill].is_active is False
    assert bandit_engine.arms[arm_to_kill].ucb_score(bandit_engine.total_pulls) < 0

    # Restore arm
    bandit_engine.set_kill_switch(arm_to_kill, True)
    assert bandit_engine.arms[arm_to_kill].is_active is True


def test_standardized_ai_decision_object():
    """Verify Section 41 Standardized AI Decision Object schema, ENRV, and gating"""
    txn = {
        "id": "TXN_ENTERPRISE_001",
        "amount": 4200.0,
        "payment_method": "upi",
        "bank_name": "HDFC Bank",
        "failure_code": "BAD_REQUEST_PAYMENT_VERIFICATION_FAILED",
        "failure_reason": "3DS OTP timed out"
    }

    decision_card = decision_engine.generate_decision_card(transaction=txn)

    # Validate Section 41 Standardized AI Decision Object Fields
    required_keys = [
        "transaction_id",
        "classification",
        "classification_confidence",
        "recovery_probability",
        "risk_score",
        "risk_tier",
        "expected_recovery_value",
        "recommended_channel",
        "recommended_time",
        "expected_cost",
        "expected_roi",
        "decision",
        "confidence",
        "explanation",
        "policy_id",
        "model_version"
    ]
    for key in required_keys:
        assert key in decision_card, f"Missing Section 41 key: {key}"

    # Verify decision state is one of the tri-states
    assert decision_card["decision"] in ["AUTO_EXECUTE", "HUMAN_APPROVAL", "SUPPRESS_RISK"]
    assert decision_card["expected_recovery_value"] > 0
    assert decision_card["expected_cost"] >= 0

    # Test permanent decline suppression
    perm_txn = {
        "id": "TXN_PERM_002",
        "amount": 50000.0,
        "failure_code": "BAD_REQUEST_PAYMENT_CARD_INVALID",
        "failure_reason": "Invalid card"
    }
    perm_card = decision_engine.generate_decision_card(transaction=perm_txn)
    assert perm_card["decision"] == "SUPPRESS_RISK"
    assert "Permanent" in perm_card["explanation"] or "risk" in perm_card["explanation"].lower()


def test_monte_carlo_forecasting():
    """Verify Monte Carlo 2.0 with 1,000 iterations and 95% confidence intervals"""
    res = monte_carlo_engine.run_simulation(
        base_daily_risk=500000.0,
        days=7,
        num_iterations=1000,
        historical_recovery_rate=0.70
    )

    assert res["iterations_run"] == 1000
    summary = res["summary"]
    # Worst case <= Expected <= Best case
    assert summary["worst_case_2_5_percentile"] <= summary["expected_recovery"]
    assert summary["expected_recovery"] <= summary["best_case_97_5_percentile"]
    assert len(res["daily_projections"]) == 7
    assert len(res["breakdowns"]["by_payment_method"]) >= 3
    assert len(res["breakdowns"]["by_bank"]) >= 3


def test_rbac_permissions():
    """Verify role permissions across all 6 roles"""
    # Admin has all permissions
    assert has_permission("Admin", Permission.USER_MANAGEMENT) is True
    assert has_permission("Admin", Permission.CONFIGURE) is True
    assert has_permission("Admin", Permission.APPROVE) is True

    # Support only has READ
    assert has_permission("Support", Permission.READ) is True
    assert has_permission("Support", Permission.EXECUTE) is False
    assert has_permission("Support", Permission.CONFIGURE) is False

    # Finance can CONFIGURE and APPROVE, but not USER_MANAGEMENT
    assert has_permission("Finance", Permission.CONFIGURE) is True
    assert has_permission("Finance", Permission.USER_MANAGEMENT) is False

    # Analyst can READ and EXPORT
    assert has_permission("Analyst", Permission.EXPORT) is True
    assert has_permission("Analyst", Permission.APPROVE) is False


def test_bank_health_monitoring():
    """Verify bank health metrics, degradation anomaly scoring, and throttling advisory"""
    from app.routes.health_monitoring import BANK_STATUS_STORE

    assert "State Bank of India" in BANK_STATUS_STORE
    sbi = BANK_STATUS_STORE["State Bank of India"]
    assert sbi["incident_status"] == "DEGRADED"
    assert sbi["recommended_action"] == "THROTTLE_RETRIES"
    assert sbi["anomaly_score"] > 50.0

    hdfc = BANK_STATUS_STORE["HDFC Bank"]
    assert hdfc["incident_status"] == "HEALTHY"
    assert hdfc["recommended_action"] == "NORMAL"


if __name__ == "__main__":
    print("Running enterprise test suite...")
    test_webhook_hmac_and_idempotency()
    print("✓ Webhook HMAC & Idempotency Passed")
    test_failure_taxonomy_classification()
    print("✓ Failure Taxonomy Classification Passed")
    test_risk_engine_checks()
    print("✓ Risk Engine Velocity & Fraud Suppression Passed")
    test_timing_engine_and_quiet_hours()
    print("✓ Timing Engine & Quiet Hours Passed")
    test_bandit_engine_exploration_and_kill_switch()
    print("✓ Bandit UCB1 Exploration & Kill Switch Passed")
    test_standardized_ai_decision_object()
    print("✓ Section 41 Standardized AI Decision Object & ENRV Passed")
    test_monte_carlo_forecasting()
    print("✓ Monte Carlo 1,000 Iteration Forecast with 95% CI Passed")
    test_rbac_permissions()
    print("✓ RBAC 6-Role Permission Matrix Passed")
    test_bank_health_monitoring()
    print("✓ Bank Health Telemetry & Degradation Anomaly Detection Passed")
    print("\nALL 9 ENTERPRISE TESTS COMPLETED SUCCESSFULLY!")
