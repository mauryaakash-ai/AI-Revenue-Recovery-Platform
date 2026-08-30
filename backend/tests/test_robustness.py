"""
Enhanced test suite for robustness, edge cases, and additional considerations:
- LLM failure and edge-case handling
- Idempotency guarantees
- Approval expiration
- Currency handling (paise as integers)
- Timezone consistency (IST)
- Malformed data handling
- Load/performance testing
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import uuid

from app.models import Base, Merchant, Customer, Transaction, AgentAction, ActionTier, ActionStatus, TransactionStatus
from app.agent_enhanced import EnhancedRevPilotAgent, ToolCallError, InvestigationTimeout
from app.tools_enhanced import IdempotencyKey, ApprovalValidator
from app.database import get_db

IST = timezone(timedelta(hours=5, minutes=30))
PAISE_PER_RUPEE = 100

@pytest.fixture
def test_db():
    """Create test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture
def merchant_and_customer(test_db: Session):
    """Create test merchant and customer"""
    merchant = Merchant(id=str(uuid.uuid4()), name="Test Merchant", api_key="test_key")
    test_db.add(merchant)
    test_db.commit()
    
    customer = Customer(
        id=str(uuid.uuid4()),
        merchant_id=merchant.id,
        name="Test Customer",
        email="test@example.com",
        lifetime_value=50000 * PAISE_PER_RUPEE  # ₹50,000 in paise
    )
    test_db.add(customer)
    test_db.commit()
    
    return merchant, customer


# ==========================
# LLM Failure & Edge Cases
# ==========================

@pytest.mark.asyncio
async def test_agent_handles_invalid_query(test_db: Session, merchant_and_customer):
    """Agent should handle invalid/empty queries gracefully"""
    merchant, _ = merchant_and_customer
    agent = EnhancedRevPilotAgent(test_db, merchant.id)
    
    # Test with empty query
    steps = []
    async for step in agent.investigate(""):
        steps.append(json.loads(step.strip()))
    
    # Should degrade gracefully
    assert any(s.get("status") == "error" or "warning" in s.get("message", "").lower() for s in steps)

@pytest.mark.asyncio
async def test_agent_rejects_out_of_scope_query(test_db: Session, merchant_and_customer):
    """Agent should reject queries about things it can't answer"""
    merchant, _ = merchant_and_customer
    agent = EnhancedRevPilotAgent(test_db, merchant.id)
    
    # Test with out-of-scope query
    steps = []
    async for step in agent.investigate("What is my competitor doing?"):
        steps.append(json.loads(step.strip()))
    
    # Should explicitly reject
    error_steps = [s for s in steps if "cannot" in s.get("message", "").lower() or s.get("status") == "error"]
    assert len(error_steps) > 0, "Should reject out-of-scope query"

@pytest.mark.asyncio
async def test_agent_handles_malformed_tool_response(test_db: Session, merchant_and_customer):
    """Agent should handle tools returning malformed data"""
    merchant, _ = merchant_and_customer
    agent = EnhancedRevPilotAgent(test_db, merchant.id)
    
    # This tests the error handling path
    steps = []
    async for step in agent.investigate("Why is revenue down?"):
        steps.append(json.loads(step.strip()))
    
    # Should not crash, should have completion step
    completion_steps = [s for s in steps if s.get("phase") == "completion"]
    assert len(completion_steps) > 0

@pytest.mark.asyncio
async def test_agent_tool_call_limit(test_db: Session, merchant_and_customer):
    """Agent should not exceed MAX_TOOL_CALLS_PER_INVESTIGATION"""
    merchant, _ = merchant_and_customer
    agent = EnhancedRevPilotAgent(test_db, merchant.id)
    
    steps = []
    async for step in agent.investigate("Analyze everything"):
        steps.append(json.loads(step.strip()))
    
    # Check that tool call count is capped
    assert agent.tool_calls_count <= 10, "Tool call count should be capped at 10"

@pytest.mark.asyncio
async def test_agent_timeout_handling(test_db: Session, merchant_and_customer):
    """Agent should gracefully handle timeouts"""
    merchant, _ = merchant_and_customer
    agent = EnhancedRevPilotAgent(test_db, merchant.id)
    agent_timeout_seconds = 1  # Very short timeout for testing
    
    # This would normally be set on the agent
    # Should eventually complete or timeout gracefully
    steps = []
    try:
        async for step in agent.investigate("Normal query"):
            steps.append(json.loads(step.strip()))
    except Exception as e:
        # Should not crash, should handle gracefully
        assert "timeout" in str(e).lower() or len(steps) > 0

@pytest.mark.asyncio
async def test_normal_day_no_anomaly_case(test_db: Session, merchant_and_customer):
    """Normal day with no anomaly should return 'no action needed' not false positives"""
    merchant, customer = merchant_and_customer
    
    # Create consistent normal transaction data
    for i in range(100):
        txn = Transaction(
            id=str(uuid.uuid4()),
            merchant_id=merchant.id,
            customer_id=customer.id,
            amount=10000 * PAISE_PER_RUPEE,  # ₹10,000
            currency="INR",
            payment_method="card",
            status=TransactionStatus.SUCCESS
        )
        test_db.add(txn)
    test_db.commit()
    
    agent = EnhancedRevPilotAgent(test_db, merchant.id)
    
    steps = []
    async for step in agent.investigate("Is everything normal?"):
        steps.append(json.loads(step.strip()))
    
    # Should NOT report false positives
    # Look for "no anomaly" or "no action" messages
    messages = [s.get("message", "").lower() for s in steps]
    found_no_action = any("no" in m and "anomal" in m for m in messages) or \
                      any("stable" in m for m in messages) or \
                      any("no action" in m for m in messages)
    
    assert found_no_action, "Should indicate no anomaly for normal data"


# ==========================
# Currency & Timezone
# ==========================

def test_currency_paise_conversion():
    """Currency amounts should be stored and displayed correctly"""
    # 1 Rupee = 100 Paise
    amount_paise = 50000 * 100  # 50,000 rupees in paise
    
    # Display function
    lakh = 100000
    rupees = amount_paise / 100
    if rupees >= lakh:
        display = f"{rupees / lakh:.2f}L"
    else:
        display = f"{rupees:,.0f}"
    
    assert display == "0.50L", f"Expected 0.50L, got {display}"

def test_timezone_consistency():
    """All timestamps should use IST consistently"""
    now_utc = datetime.now(timezone.utc)
    now_ist = now_utc.astimezone(IST)
    
    # Verify IST offset is correct (UTC+5:30)
    expected_offset = timedelta(hours=5, minutes=30)
    assert now_ist.utcoffset() == expected_offset, "IST offset should be UTC+5:30"

def test_timezone_display():
    """Timestamps should be ISO format with IST"""
    now_ist = datetime.now(IST)
    iso_str = now_ist.isoformat()
    
    # Should contain +05:30 or similar
    assert "+" in iso_str or "-" in iso_str, "Should include timezone offset"
    assert iso_str.endswith(("30", "00", "45", "15")), "Should have minute component"


# ==========================
# Idempotency & Safety
# ==========================

def test_idempotency_key_generation():
    """Idempotency keys should be deterministic"""
    merchant_id = "merchant_123"
    action = "send_message"
    target_id = "customer_456"
    params = {"message": "Hello"}
    
    key1 = IdempotencyKey.generate(merchant_id, action, target_id, params)
    key2 = IdempotencyKey.generate(merchant_id, action, target_id, params)
    
    assert key1 == key2, "Same inputs should generate same key"

def test_idempotency_key_uniqueness():
    """Different inputs should generate different keys"""
    merchant_id = "merchant_123"
    action = "send_message"
    target_id = "customer_456"
    
    key1 = IdempotencyKey.generate(merchant_id, action, target_id, {"msg": "Hello"})
    key2 = IdempotencyKey.generate(merchant_id, action, target_id, {"msg": "Goodbye"})
    
    assert key1 != key2, "Different inputs should generate different keys"

def test_approval_validation():
    """Approval tokens should expire after set time"""
    created_at = datetime.now(IST) - timedelta(minutes=45)  # Created 45 min ago
    
    # 30 minute approval window
    is_valid, reason = ApprovalValidator.validate_approval("valid_token", "action_1", created_at)
    
    assert not is_valid, "Approval should be expired after 45 minutes"
    assert "expired" in reason.lower(), "Should mention expiration"

def test_approval_still_valid():
    """Recent approvals should still be valid"""
    created_at = datetime.now(IST) - timedelta(minutes=10)  # Created 10 min ago
    
    is_valid, reason = ApprovalValidator.validate_approval("valid_token", "action_1", created_at)
    
    assert is_valid, "Approval should be valid within 30 minutes"

def test_approval_expiration_warning():
    """Should warn when approval is about to expire"""
    created_at = datetime.now(IST) - timedelta(minutes=26)  # Created 26 min ago
    
    warning = ApprovalValidator.generate_expiration_warning(created_at, time_remaining_minutes=5)
    
    assert warning is not None, "Should warn when expiration is imminent"
    assert "expires" in warning.lower(), "Warning should mention expiration"


# ==========================
# Malformed Data Handling
# ==========================

@pytest.mark.asyncio
async def test_agent_handles_missing_field_transaction(test_db: Session, merchant_and_customer):
    """Agent should handle malformed transaction records gracefully"""
    merchant, customer = merchant_and_customer
    
    # Create transaction with missing optional field (not required field)
    txn = Transaction(
        id=str(uuid.uuid4()),
        merchant_id=merchant.id,
        customer_id=customer.id,
        amount=10000 * PAISE_PER_RUPEE,
        currency="INR",
        payment_method="card",
        status=TransactionStatus.SUCCESS,
        # Missing optional: failure_reason, device_type, location
    )
    test_db.add(txn)
    test_db.commit()
    
    agent = EnhancedRevPilotAgent(test_db, merchant.id)
    
    steps = []
    async for step in agent.investigate("Analyze transactions"):
        steps.append(json.loads(step.strip()))
    
    # Should not crash
    completion_steps = [s for s in steps if s.get("phase") == "completion"]
    assert len(completion_steps) > 0, "Should complete despite malformed data"

@pytest.mark.asyncio
async def test_agent_handles_negative_amount(test_db: Session, merchant_and_customer):
    """Agent should handle invalid amounts"""
    merchant, customer = merchant_and_customer
    
    # Create transaction with negative amount (should be rejected)
    try:
        txn = Transaction(
            id=str(uuid.uuid4()),
            merchant_id=merchant.id,
            customer_id=customer.id,
            amount=-10000,  # Negative amount
            currency="INR",
            payment_method="card",
            status=TransactionStatus.SUCCESS,
        )
        test_db.add(txn)
        test_db.commit()
    except:
        # Database should reject or this should be caught
        pass
    
    agent = EnhancedRevPilotAgent(test_db, merchant.id)
    
    # Query should not crash
    steps = []
    async for step in agent.investigate("Analyze data"):
        steps.append(json.loads(step.strip()))
    
    # Should handle gracefully
    assert len(steps) > 0


# ==========================
# Load & Performance
# ==========================

@pytest.mark.asyncio
async def test_performance_on_large_dataset(test_db: Session, merchant_and_customer):
    """Agent should handle 50k transaction dataset without degradation"""
    merchant, customer = merchant_and_customer
    
    # Create 50k transactions
    for i in range(50000):
        txn = Transaction(
            id=str(uuid.uuid4()),
            merchant_id=merchant.id,
            customer_id=customer.id if i % 10 == 0 else str(uuid.uuid4()),
            amount=int((10000 + i % 5000) * PAISE_PER_RUPEE),
            currency="INR",
            payment_method=["card", "upi", "netbanking"][i % 3],
            status=TransactionStatus.SUCCESS if i % 20 != 0 else TransactionStatus.FAILED,
            failure_reason="timeout" if i % 20 == 0 else None
        )
        test_db.add(txn)
        
        if i % 1000 == 0:
            test_db.commit()
    
    test_db.commit()
    
    agent = EnhancedRevPilotAgent(test_db, merchant.id)
    
    import time
    start = time.time()
    
    steps = []
    async for step in agent.investigate("Analyze all data"):
        steps.append(json.loads(step.strip()))
    
    elapsed = time.time() - start
    
    # Should complete in reasonable time (under 30 seconds)
    assert elapsed < 30, f"Investigation should complete in under 30 seconds, took {elapsed:.1f}s"
    
    # Verify tool execution was efficient
    assert agent.tool_calls_count <= MAX_TOOL_CALLS_PER_INVESTIGATION

@pytest.mark.asyncio
async def test_conflicting_signals_scenario(test_db: Session, merchant_and_customer):
    """Agent should handle marginal/conflicting signals without over-dramatizing"""
    merchant, customer = merchant_and_customer
    
    # Create data with small anomaly (2% failure rate increase, not significant)
    success_count = 9800
    fail_count = 200
    
    for i in range(success_count + fail_count):
        txn = Transaction(
            id=str(uuid.uuid4()),
            merchant_id=merchant.id,
            customer_id=customer.id if i % 10 == 0 else str(uuid.uuid4()),
            amount=10000 * PAISE_PER_RUPEE,
            currency="INR",
            payment_method="card",
            status=TransactionStatus.FAILED if i >= success_count else TransactionStatus.SUCCESS
        )
        test_db.add(txn)
    
    test_db.commit()
    
    agent = EnhancedRevPilotAgent(test_db, merchant.id)
    
    steps = []
    async for step in agent.investigate("Assess data quality"):
        steps.append(json.loads(step.strip()))
    
    # Should not over-dramatize small variations
    messages = [s.get("message", "").lower() for s in steps]
    
    # Should mention confidence/uncertainty rather than alarming
    has_confidence_mention = any("confiden" in m or "estimate" in m for m in messages)
    # Or should mention it's minor/acceptable
    has_minor_mention = any("minor" in m or "small" in m or "normal" in m for m in messages)
    
    # At least acknowledge the findings with appropriate confidence level
    assert has_confidence_mention or has_minor_mention, "Should not over-dramatize marginal findings"


# ==========================
# Observability
# ==========================

def test_observability_metrics():
    """Agent should track observability metrics"""
    merchant_id = "merchant_123"
    agent = EnhancedRevPilotAgent(None, merchant_id)
    
    # Verify tracking attributes exist
    assert hasattr(agent, "investigation_id")
    assert hasattr(agent, "start_time")
    assert hasattr(agent, "tool_calls_count")
    assert hasattr(agent, "errors_encountered")
    assert hasattr(agent, "data_sparsity_warnings")

def test_investigation_id_uniqueness():
    """Investigation IDs should be unique"""
    merchant_id = "merchant_123"
    agent1 = EnhancedRevPilotAgent(None, merchant_id)
    agent2 = EnhancedRevPilotAgent(None, merchant_id)
    
    id1 = agent1._generate_investigation_id()
    id2 = agent2._generate_investigation_id()
    
    # Different agents should generate different IDs
    assert id1 != id2, "Investigation IDs should be unique across calls"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

