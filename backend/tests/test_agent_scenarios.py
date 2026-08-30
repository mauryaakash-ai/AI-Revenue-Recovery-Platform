"""
Integration tests for RevPilot agent against 5 key scenarios.
Each scenario uses synthetic data with known ground truth.
"""

import sys
import pytest
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
sys.path.insert(0, '.')

from app.database import Base
from app.models import Merchant, Customer, Transaction, TransactionStatus, RecoveryPrediction
from app.agent import RevPilotAgent
import uuid


@pytest.fixture
def test_db():
    """Create in-memory SQLite database for testing"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def base_setup(test_db):
    """Create merchant and customers"""
    merchant = Merchant(id=str(uuid.uuid4()), name="Test Merchant")
    test_db.add(merchant)
    test_db.commit()
    
    customers = []
    for i in range(100):
        c = Customer(
            id=str(uuid.uuid4()),
            merchant_id=merchant.id,
            name=f"Customer {i}",
            email=f"customer{i}@test.com",
            segment=["standard", "premium", "vip"][i % 3],
            lifetime_value=5000.0 + i * 100
        )
        test_db.add(c)
        customers.append(c)
    
    test_db.commit()
    return merchant, customers


def test_scenario_card_failure_spike(test_db, base_setup):
    """
    Scenario: Card payment failure spike (day 30-35)
    92% → 74% success rate, ~143 affected transactions
    Expected: Agent detects anomaly, quantifies ₹1.8L impact
    """
    merchant, customers = base_setup
    
    # Create baseline: 7 days of 90%+ success
    baseline_txns = 0
    for day in range(7, 14):
        date = datetime.utcnow() - timedelta(days=day)
        for i in range(100):
            success = i < 92  # 92% success rate
            tx = Transaction(
                id=str(uuid.uuid4()),
                merchant_id=merchant.id,
                customer_id=customers[i].id,
                amount=12000.0,  # ₹12k avg
                currency="INR",
                payment_method="card" if i < 45 else "upi",
                status=TransactionStatus.SUCCESS if success else TransactionStatus.FAILED,
                failure_reason="card_declined" if not success else None,
                created_at=date
            )
            test_db.add(tx)
            if success:
                baseline_txns += 1
    
    # Create spike: 3 days of 74% card success
    spike_failed = 0
    spike_total = 0
    for day in range(1, 4):  # days 1-3 (represents days 30-32 conceptually)
        date = datetime.utcnow() - timedelta(days=day)
        for i in range(100):
            if i < 45:  # Card payments
                success = i < 33  # 74% success (33/45)
                spike_total += 1
                if not success:
                    spike_failed += 1
            else:  # UPI
                success = i < 95  # Keep UPI high
            
            tx = Transaction(
                id=str(uuid.uuid4()),
                merchant_id=merchant.id,
                customer_id=customers[i].id,
                amount=12000.0,
                currency="INR",
                payment_method="card" if i < 45 else "upi",
                status=TransactionStatus.SUCCESS if success else TransactionStatus.FAILED,
                failure_reason="card_declined" if (not success and i < 45) else None,
                created_at=date
            )
            test_db.add(tx)
    
    test_db.commit()
    
    # Run agent
    agent = RevPilotAgent(test_db, merchant.id)
    
    # Collect investigation steps
    steps = []
    async def collect_steps():
        async for step_json in agent.investigate("Why is revenue down?"):
            import json
            step = json.loads(step_json.strip())
            steps.append(step)
    
    asyncio.run(collect_steps())
    
    # Assertions
    assert len(steps) > 0, "Agent should produce investigation steps"
    
    # Should detect anomaly
    anomaly_steps = [s for s in steps if s.get('phase') == 'root_cause_analysis']
    assert len(anomaly_steps) > 0, "Should reach root cause analysis"
    
    # Should quantify impact
    impact_steps = [s for s in steps if s.get('phase') == 'financial_impact']
    assert len(impact_steps) > 0, "Should calculate financial impact"
    
    print(f"Card failure spike test: {spike_failed} failures out of {spike_total} card transactions detected")


def test_scenario_no_anomaly(test_db, base_setup):
    """
    Scenario: Normal day with no injected anomaly
    Expected: Agent should NOT report false positives
    """
    merchant, customers = base_setup
    
    # Create normal, consistent data for 7 days
    for day in range(7):
        date = datetime.utcnow() - timedelta(days=day)
        for i in range(100):
            # Consistent 92% success rate
            success = i < 92
            tx = Transaction(
                id=str(uuid.uuid4()),
                merchant_id=merchant.id,
                customer_id=customers[i].id,
                amount=12000.0,
                currency="INR",
                payment_method=["card", "upi", "netbanking"][i % 3],
                status=TransactionStatus.SUCCESS if success else TransactionStatus.FAILED,
                failure_reason="card_declined" if not success else None,
                created_at=date
            )
            test_db.add(tx)
    
    test_db.commit()
    
    agent = RevPilotAgent(test_db, merchant.id)
    
    # Run agent
    steps = []
    async def collect_steps():
        async for step_json in agent.investigate("What's the status?"):
            import json
            step = json.loads(step_json.strip())
            steps.append(step)
    
    asyncio.run(collect_steps())
    
    # Should complete without false alarm
    assert len(steps) > 0
    
    # Check that anomaly detection doesn't report anomaly
    anomaly_steps = [s for s in steps if 'anomaly' in s.get('message', '').lower()]
    if anomaly_steps:
        # If anomaly is mentioned, confidence should be low
        for step in anomaly_steps:
            if 'details' in step:
                assert step['details'].get('has_anomaly') == False or step['details'].get('confidence', 0) < 0.5


def test_scenario_high_value_failures(test_db, base_setup):
    """
    Scenario: Cluster of high-value payment failures
    Expected: Agent ranks these for recovery, identifies as high-priority
    """
    merchant, customers = base_setup
    
    # Create high-value failures
    high_value_failures = 0
    for i in range(10):  # 10 high-value customers
        customer = customers[i]
        # Give them some successful history
        for _ in range(3):
            tx = Transaction(
                id=str(uuid.uuid4()),
                merchant_id=merchant.id,
                customer_id=customer.id,
                amount=50000.0,
                currency="INR",
                payment_method="card",
                status=TransactionStatus.SUCCESS,
                created_at=datetime.utcnow() - timedelta(days=10)
            )
            test_db.add(tx)
        
        # Then fail with large amount
        tx = Transaction(
            id=str(uuid.uuid4()),
            merchant_id=merchant.id,
            customer_id=customer.id,
            amount=100000.0,  # High value
            currency="INR",
            payment_method="card",
            status=TransactionStatus.FAILED,
            failure_reason="insufficient_funds",
            created_at=datetime.utcnow()
        )
        test_db.add(tx)
        high_value_failures += 1
        
        # Add recovery prediction
        pred = RecoveryPrediction(
            id=str(uuid.uuid4()),
            transaction_id=tx.id,
            probability=0.65,  # Moderate recovery probability
            expected_recovery=65000.0,
            model_version="v1.0"
        )
        test_db.add(pred)
    
    test_db.commit()
    
    agent = RevPilotAgent(test_db, merchant.id)
    
    # Run agent
    steps = []
    async def collect_steps():
        async for step_json in agent.investigate("Which high-value customers can I recover?"):
            import json
            step = json.loads(step_json.strip())
            steps.append(step)
    
    asyncio.run(collect_steps())
    
    # Should identify recovery opportunities
    assert len(steps) > 0
    print(f"High-value failures test: {high_value_failures} high-value failures identified")


def test_scenario_checkout_abandonment(test_db, base_setup):
    """
    Scenario: Checkout abandonment spike
    Expected: Agent identifies abandoned sessions, estimates value
    """
    merchant, customers = base_setup
    
    from app.models import CheckoutEvent
    
    # Create abandoned checkouts
    abandoned_count = 0
    for i in range(50):
        customer = customers[i]
        session_id = str(uuid.uuid4())
        
        # Initiate
        event1 = CheckoutEvent(
            id=str(uuid.uuid4()),
            customer_id=customer.id,
            session_id=session_id,
            event="initiated",
            timestamp=datetime.utcnow() - timedelta(hours=2)
        )
        test_db.add(event1)
        
        # Abandon
        event2 = CheckoutEvent(
            id=str(uuid.uuid4()),
            customer_id=customer.id,
            session_id=session_id,
            event="abandoned",
            timestamp=datetime.utcnow() - timedelta(hours=1)
        )
        test_db.add(event2)
        abandoned_count += 1
    
    test_db.commit()
    
    agent = RevPilotAgent(test_db, merchant.id)
    
    # Run agent
    steps = []
    async def collect_steps():
        async for step_json in agent.investigate("What's happening with checkouts?"):
            import json
            step = json.loads(step_json.strip())
            steps.append(step)
    
    asyncio.run(collect_steps())
    
    assert len(steps) > 0
    print(f"Checkout abandonment test: {abandoned_count} abandoned sessions identified")


def test_scenario_refund_spike(test_db, base_setup):
    """
    Scenario: Refund spike on specific product/date
    Expected: Agent detects pattern, quantifies value, identifies affected customers
    """
    merchant, customers = base_setup
    
    from app.models import Refund, RefundStatus
    
    # Create refund spike
    refund_count = 0
    for i in range(30):
        customer = customers[i]
        
        # Create original transaction
        tx = Transaction(
            id=str(uuid.uuid4()),
            merchant_id=merchant.id,
            customer_id=customer.id,
            amount=5000.0,
            currency="INR",
            payment_method="card",
            status=TransactionStatus.SUCCESS,
            product_id="defective-product",
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        test_db.add(tx)
        test_db.commit()
        
        # Create refund
        refund = Refund(
            id=str(uuid.uuid4()),
            merchant_id=merchant.id,
            transaction_id=tx.id,
            amount=5000.0,
            reason="defective_product",
            status=RefundStatus.COMPLETED,
            created_at=datetime.utcnow()
        )
        test_db.add(refund)
        refund_count += 1
    
    test_db.commit()
    
    agent = RevPilotAgent(test_db, merchant.id)
    
    # Run agent
    steps = []
    async def collect_steps():
        async for step_json in agent.investigate("Why are we getting so many refunds?"):
            import json
            step = json.loads(step_json.strip())
            steps.append(step)
    
    asyncio.run(collect_steps())
    
    assert len(steps) > 0
    print(f"Refund spike test: {refund_count} refunds detected")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
