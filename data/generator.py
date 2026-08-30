"""
Synthetic data generator for RevPilot.
Generates realistic transaction data with injected anomalies.
"""

import sys
import os
import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import numpy as np

# Add parent to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app.database import SessionLocal, engine, Base
from backend.app.models import (
    Merchant, Customer, Transaction, Refund, Settlement, CheckoutEvent,
    RecoveryPrediction, TransactionStatus, RefundStatus, SettlementStatus
)


class SyntheticDataGenerator:
    def __init__(self, seed: int = 42, days: int = 90):
        self.seed = seed
        self.days = days
        self.random_gen = random.Random(seed)
        self.np_gen = np.random.RandomState(seed)
        
        # Configuration
        self.num_merchants = 1
        self.num_customers = 5000
        self.num_products = 500
        self.num_transactions = 50000
        
        # Baseline metrics
        self.avg_daily_revenue = 900000  # ₹9L
        self.baseline_success_rate = 0.92
        
    def generate_all(self):
        """Generate and insert all synthetic data"""
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        db = SessionLocal()
        try:
            print(f"Generating data with seed={self.seed}...")
            
            # Generate entities
            merchants = self._generate_merchants()
            print(f"✓ Generated {len(merchants)} merchants")
            
            customers = self._generate_customers(merchants)
            print(f"✓ Generated {len(customers)} customers")
            
            products = self._generate_products()
            print(f"✓ Generated {len(products)} products")
            
            transactions = self._generate_transactions(merchants, customers, products)
            print(f"✓ Generated {len(transactions)} transactions")
            
            refunds = self._generate_refunds(merchants, transactions)
            print(f"✓ Generated {len(refunds)} refunds")
            
            settlements = self._generate_settlements(merchants)
            print(f"✓ Generated {len(settlements)} settlements")
            
            checkout_events = self._generate_checkout_events(customers)
            print(f"✓ Generated {len(checkout_events)} checkout events")
            
            recovery_predictions = self._generate_recovery_predictions(transactions)
            print(f"✓ Generated {len(recovery_predictions)} recovery predictions")
            
            # Bulk insert
            print("\nInserting into database...")
            db.bulk_save_objects(merchants)
            db.commit()
            
            db.bulk_save_objects(customers)
            db.commit()
            
            db.bulk_save_objects(transactions)
            db.commit()
            
            db.bulk_save_objects(refunds)
            db.commit()
            
            db.bulk_save_objects(settlements)
            db.commit()
            
            db.bulk_save_objects(checkout_events)
            db.commit()
            
            db.bulk_save_objects(recovery_predictions)
            db.commit()
            
            print("✓ Data inserted successfully")
            print(f"\nSynthetic dataset complete:")
            print(f"  - {len(merchants)} merchants")
            print(f"  - {len(customers)} customers")
            print(f"  - {len(products)} products")
            print(f"  - {len(transactions)} transactions")
            print(f"  - {len(refunds)} refunds")
            print(f"  - {len(settlements)} settlements")
            print(f"  - {len(checkout_events)} checkout events")
            
        finally:
            db.close()
    
    def _generate_merchants(self) -> List[Merchant]:
        merchants = []
        for i in range(self.num_merchants):
            merchant = Merchant(
                id=str(uuid.uuid4()),
                name=f"Merchant {i+1}",
                api_key=str(uuid.uuid4())
            )
            merchants.append(merchant)
        return merchants
    
    def _generate_customers(self, merchants: List[Merchant]) -> List[Customer]:
        customers = []
        for i in range(self.num_customers):
            ltv = self.np_gen.exponential(scale=5000)  # Realistic LTV distribution
            customer = Customer(
                id=str(uuid.uuid4()),
                merchant_id=merchants[0].id,
                name=f"Customer {i+1}",
                email=f"customer{i+1}@example.com",
                segment=self.random_gen.choice(["standard", "premium", "vip"]),
                lifetime_value=ltv,
                created_at=datetime.utcnow() - timedelta(days=self.np_gen.randint(0, self.days))
            )
            customers.append(customer)
        return customers
    
    def _generate_products(self) -> List[Dict]:
        """Generate product IDs (not persisted, just for reference)"""
        return [str(uuid.uuid4()) for _ in range(self.num_products)]
    
    def _generate_transactions(self, merchants: List[Merchant], customers: List[Customer], products: List[str]) -> List[Transaction]:
        """
        Generate transactions with injected anomalies:
        - Card payment failure spike (day 30-35)
        - UPI success rate drop (day 45-50)
        - High-value payment failures (scattered)
        - Refund spike (day 60-65)
        - Checkout abandonment pattern (throughout)
        - Customer churn pattern (throughout)
        - Weekend seasonality
        - One unusual volume spike
        """
        transactions = []
        merchant = merchants[0]
        
        # Base load: distribute evenly across days
        transactions_per_day = self.num_transactions // self.days
        
        for day in range(self.days):
            date = datetime.utcnow() - timedelta(days=self.days - day)
            date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Weekend seasonality: boost on weekends
            is_weekend = date.weekday() >= 5
            day_factor = 1.3 if is_weekend else 1.0
            
            # Anomaly: Day 70 (unusual volume spike)
            if day == 70:
                day_factor *= 1.8
            
            day_transactions = int(transactions_per_day * day_factor)
            
            for _ in range(day_transactions):
                customer = self.random_gen.choice(customers)
                product = self.random_gen.choice(products)
                # Use numpy's choice with probabilities for proper weighted selection
                payment_method = self.np_gen.choice(["card", "upi", "netbanking", "wallet"], p=[0.45, 0.35, 0.15, 0.05])
                
                # Base success rate
                success_rate = self.baseline_success_rate
                
                # Card payment failure spike (day 30-35): 92% -> 74%
                if 30 <= day <= 35 and payment_method == "card":
                    success_rate = 0.74
                
                # UPI success rate drop (day 45-50): 95% -> 82%
                if 45 <= day <= 50 and payment_method == "upi":
                    success_rate = 0.82
                
                # Random failure
                is_success = self.random_gen.random() < success_rate
                
                # Amount distribution: most small, some large
                if self.random_gen.random() < 0.1:  # 10% high-value
                    amount = self.np_gen.exponential(scale=10000)
                else:
                    amount = self.np_gen.exponential(scale=2000)
                
                # Failure reason
                failure_reason = None
                if not is_success:
                    reasons = ["insufficient_funds", "card_declined", "invalid_cvv", "timeout", "network_error", "3ds_failed"]
                    failure_reason = self.random_gen.choice(reasons)
                
                # Slight time randomization within day
                hour = self.np_gen.randint(0, 24)
                minute = self.np_gen.randint(0, 60)
                second = self.np_gen.randint(0, 60)
                tx_date = date.replace(hour=hour, minute=minute, second=second)
                
                transaction = Transaction(
                    id=str(uuid.uuid4()),
                    merchant_id=merchant.id,
                    customer_id=customer.id,
                    amount=max(10, amount),
                    currency="INR",
                    payment_method=payment_method,
                    status=TransactionStatus.SUCCESS if is_success else TransactionStatus.FAILED,
                    failure_reason=failure_reason,
                    product_id=product,
                    order_id=str(uuid.uuid4()),
                    device_type=self.random_gen.choice(["mobile", "desktop", "tablet"]),
                    location=self.random_gen.choice(["Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai"]),
                    created_at=tx_date
                )
                transactions.append(transaction)
        
        return transactions
    
    def _generate_refunds(self, merchants: List[Merchant], transactions: List[Transaction]) -> List[Refund]:
        """Generate refunds with a spike around day 60-65"""
        refunds = []
        merchant = merchants[0]
        
        # Find successful transactions
        successful_txs = [t for t in transactions if t.status == TransactionStatus.SUCCESS]
        
        # Base refund rate
        base_refund_rate = 0.05
        
        for i, tx in enumerate(successful_txs):
            # Refund spike: day 60-65
            refund_rate = base_refund_rate
            if hasattr(tx, 'created_at'):
                days_ago = (datetime.utcnow() - tx.created_at).days
                if 30 <= days_ago <= 35:  # Roughly day 60-65
                    refund_rate = 0.15
            
            if self.random_gen.random() < refund_rate:
                refund = Refund(
                    id=str(uuid.uuid4()),
                    merchant_id=merchant.id,
                    transaction_id=tx.id,
                    amount=tx.amount,
                    reason=self.random_gen.choice(["customer_request", "defective_product", "duplicate_charge", "other"]),
                    status=self.random_gen.choice([RefundStatus.COMPLETED, RefundStatus.PENDING]),
                    created_at=tx.created_at + timedelta(hours=self.np_gen.randint(1, 48))
                )
                refunds.append(refund)
        
        return refunds
    
    def _generate_settlements(self, merchants: List[Merchant]) -> List[Settlement]:
        """Generate daily settlements"""
        settlements = []
        merchant = merchants[0]
        
        for day in range(self.days):
            settlement_date = datetime.utcnow() - timedelta(days=self.days - day)
            settlement_date = settlement_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            settlement = Settlement(
                id=str(uuid.uuid4()),
                merchant_id=merchant.id,
                amount=self.avg_daily_revenue * self.random_gen.uniform(0.9, 1.1),
                status=SettlementStatus.COMPLETED if day > 3 else SettlementStatus.PENDING,
                settlement_date=settlement_date
            )
            settlements.append(settlement)
        
        return settlements
    
    def _generate_checkout_events(self, customers: List[Customer]) -> List[CheckoutEvent]:
        """Generate checkout events (initiations, completions, abandonments)"""
        events = []
        
        # Each customer has some checkout events
        for customer in customers:
            num_events = self.np_gen.randint(1, 20)
            for _ in range(num_events):
                session_id = str(uuid.uuid4())
                event_date = datetime.utcnow() - timedelta(days=self.np_gen.randint(0, self.days))
                
                # Initiation event
                events.append(CheckoutEvent(
                    id=str(uuid.uuid4()),
                    customer_id=customer.id,
                    session_id=session_id,
                    event="initiated",
                    timestamp=event_date
                ))
                
                # Completion or abandonment
                if self.random_gen.random() < 0.7:  # 70% completion
                    events.append(CheckoutEvent(
                        id=str(uuid.uuid4()),
                        customer_id=customer.id,
                        session_id=session_id,
                        event="completed",
                        timestamp=event_date + timedelta(minutes=self.np_gen.randint(1, 30))
                    ))
                else:
                    events.append(CheckoutEvent(
                        id=str(uuid.uuid4()),
                        customer_id=customer.id,
                        session_id=session_id,
                        event="abandoned",
                        timestamp=event_date + timedelta(minutes=self.np_gen.randint(1, 60))
                    ))
        
        return events
    
    def _generate_recovery_predictions(self, transactions: List[Transaction]) -> List[RecoveryPrediction]:
        """Generate recovery predictions for failed transactions"""
        predictions = []
        
        failed_txs = [t for t in transactions if t.status == TransactionStatus.FAILED]
        
        for tx in failed_txs:
            # Simple heuristic: probability based on amount and failure reason
            probability = self.np_gen.uniform(0.2, 0.9)
            
            # Lower probability for timeout, higher for card issues
            if tx.failure_reason == "timeout":
                probability *= 0.7
            elif tx.failure_reason in ["insufficient_funds", "3ds_failed"]:
                probability *= 1.1
            
            probability = min(1.0, max(0.0, probability))
            
            prediction = RecoveryPrediction(
                id=str(uuid.uuid4()),
                transaction_id=tx.id,
                probability=probability,
                expected_recovery=tx.amount * probability,
                model_version="v1.0"
            )
            predictions.append(prediction)
        
        return predictions


def generate_demo_snapshot(merchant_id: str):
    """Generate a consistent demo snapshot with known values"""
    db = SessionLocal()
    try:
        # This will seed the demo data for reproducible demo runs
        print("Demo snapshot generation stubbed for Phase 2")
    finally:
        db.close()


if __name__ == "__main__":
    generator = SyntheticDataGenerator(seed=42, days=90)
    generator.generate_all()
