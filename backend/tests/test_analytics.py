"""
Unit tests for analytics layer.
Tests all functions independently with known ground truth from synthetic data.
"""

import sys
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
sys.path.insert(0, '.')

from app.database import Base
from app.models import Merchant, Customer, Transaction, TransactionStatus, RecoveryPrediction
from app.analytics import AnalyticsEngine
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
def merchant_and_customers(test_db):
    """Create test merchant and customers"""
    merchant = Merchant(id=str(uuid.uuid4()), name="Test Merchant")
    test_db.add(merchant)
    test_db.commit()
    
    customers = []
    for i in range(5):
        c = Customer(
            id=str(uuid.uuid4()),
            merchant_id=merchant.id,
            name=f"Customer {i}",
            email=f"customer{i}@test.com",
            segment="standard",
            lifetime_value=10000.0 + i * 1000
        )
        test_db.add(c)
        customers.append(c)
    
    test_db.commit()
    return merchant, customers


def test_get_revenue_with_no_transactions(test_db, merchant_and_customers):
    """Test revenue calculation with no transactions"""
    merchant, _ = merchant_and_customers
    
    result = AnalyticsEngine.get_revenue(test_db, merchant.id, days=7)
    
    assert result['total_revenue'] == 0.0
    assert result['today_revenue'] == 0.0
    assert result['yesterday_revenue'] == 0.0
    assert result['delta'] == 0.0
    assert result['delta_percentage'] == 0.0


def test_get_revenue_with_transactions(test_db, merchant_and_customers):
    """Test revenue calculation with transactions"""
    merchant, customers = merchant_and_customers
    
    # Create transactions
    for i in range(5):
        tx = Transaction(
            id=str(uuid.uuid4()),
            merchant_id=merchant.id,
            customer_id=customers[i].id,
            amount=1000.0 + i * 100,
            currency="INR",
            payment_method="card",
            status=TransactionStatus.SUCCESS,
            created_at=datetime.utcnow()
        )
        test_db.add(tx)
    
    test_db.commit()
    
    result = AnalyticsEngine.get_revenue(test_db, merchant.id, days=7)
    
    assert result['total_revenue'] > 0
    assert result['today_revenue'] > 0


def test_get_payment_success_rate(test_db, merchant_and_customers):
    """Test success rate calculation"""
    merchant, customers = merchant_and_customers
    
    # 8 successful, 2 failed
    for i in range(8):
        tx = Transaction(
            id=str(uuid.uuid4()),
            merchant_id=merchant.id,
            customer_id=customers[i % 5].id,
            amount=1000.0,
            currency="INR",
            payment_method="card",
            status=TransactionStatus.SUCCESS,
            created_at=datetime.utcnow()
        )
        test_db.add(tx)
    
    for i in range(2):
        tx = Transaction(
            id=str(uuid.uuid4()),
            merchant_id=merchant.id,
            customer_id=customers[i].id,
            amount=1000.0,
            currency="INR",
            payment_method="card",
            status=TransactionStatus.FAILED,
            failure_reason="card_declined",
            created_at=datetime.utcnow()
        )
        test_db.add(tx)
    
    test_db.commit()
    
    result = AnalyticsEngine.get_payment_success_rate(test_db, merchant.id, days=7)
    
    assert result['total'] == 10
    assert result['successful'] == 8
    assert result['failed'] == 2
    assert abs(result['success_rate'] - 80.0) < 0.1


def test_get_failed_payments(test_db, merchant_and_customers):
    """Test failed payment analysis"""
    merchant, customers = merchant_and_customers
    
    # Create failures with different reasons
    reasons = ["insufficient_funds", "card_declined", "timeout"]
    for i, reason in enumerate(reasons):
        for _ in range(2):
            tx = Transaction(
                id=str(uuid.uuid4()),
                merchant_id=merchant.id,
                customer_id=customers[i].id,
                amount=500.0 + _ * 100,
                currency="INR",
                payment_method="card",
                status=TransactionStatus.FAILED,
                failure_reason=reason,
                created_at=datetime.utcnow()
            )
            test_db.add(tx)
    
    test_db.commit()
    
    result = AnalyticsEngine.get_failed_payments(test_db, merchant.id, days=7)
    
    assert result['total_failed'] == 6
    assert 'insufficient_funds' in result['by_reason']
    assert 'card_declined' in result['by_reason']
    assert 'timeout' in result['by_reason']


def test_get_customers(test_db, merchant_and_customers):
    """Test customer statistics"""
    merchant, customers = merchant_and_customers
    
    result = AnalyticsEngine.get_customers(test_db, merchant.id)
    
    assert result['total_customers'] == 5
    assert result['total_ltv'] > 0
    assert result['avg_ltv'] > 0
    assert 'standard' in result['by_segment']


def test_detect_anomalies_no_anomaly(test_db, merchant_and_customers):
    """Test anomaly detection on normal data"""
    merchant, customers = merchant_and_customers
    
    # Create transactions consistently
    base_amount = 10000.0
    for day in range(8):
        for i in range(10):
            date = datetime.utcnow() - timedelta(days=day)
            tx = Transaction(
                id=str(uuid.uuid4()),
                merchant_id=merchant.id,
                customer_id=customers[i % 5].id,
                amount=base_amount,
                currency="INR",
                payment_method="card",
                status=TransactionStatus.SUCCESS,
                created_at=date
            )
            test_db.add(tx)
    
    test_db.commit()
    
    result = AnalyticsEngine.detect_anomalies(test_db, merchant.id, baseline_days=7)
    
    # Should not detect anomaly on normal data
    assert result['has_anomaly'] == False
    assert result['confidence'] < 0.3


def test_calculate_revenue_loss(test_db, merchant_and_customers):
    """Test revenue loss calculation"""
    merchant, customers = merchant_and_customers
    
    # Create failed transactions
    for i in range(5):
        tx = Transaction(
            id=str(uuid.uuid4()),
            merchant_id=merchant.id,
            customer_id=customers[i].id,
            amount=1000.0,
            currency="INR",
            payment_method="card",
            status=TransactionStatus.FAILED,
            failure_reason="card_declined",
            created_at=datetime.utcnow()
        )
        test_db.add(tx)
    
    test_db.commit()
    
    result = AnalyticsEngine.calculate_revenue_loss(test_db, merchant.id, days=7)
    
    assert result['failed_transactions'] == 5
    assert result['revenue_lost'] == 5000.0
    assert result['confidence'] == 1.0


def test_recovery_probability(test_db, merchant_and_customers):
    """Test recovery probability prediction"""
    merchant, customers = merchant_and_customers
    
    # Create transaction and prediction
    tx = Transaction(
        id=str(uuid.uuid4()),
        merchant_id=merchant.id,
        customer_id=customers[0].id,
        amount=1000.0,
        currency="INR",
        payment_method="card",
        status=TransactionStatus.FAILED,
        failure_reason="card_declined",
        created_at=datetime.utcnow()
    )
    test_db.add(tx)
    test_db.commit()
    
    pred = RecoveryPrediction(
        id=str(uuid.uuid4()),
        transaction_id=tx.id,
        probability=0.75,
        expected_recovery=750.0,
        model_version="v1.0"
    )
    test_db.add(pred)
    test_db.commit()
    
    result = AnalyticsEngine.predict_recovery_probability(test_db, tx.id)
    
    assert result['probability'] == 0.75
    assert result['expected_recovery'] == 750.0


def test_segment_customers(test_db, merchant_and_customers):
    """Test customer segmentation"""
    merchant, _ = merchant_and_customers
    
    result = AnalyticsEngine.segment_customers(test_db, merchant.id)
    
    assert result['total_customers'] == 5
    assert 'standard' in result['segments']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
