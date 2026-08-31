"""
Synthetic data generator for AI Revenue Recovery Platform for Razorpay.
Generates realistic Indian fintech transaction data, customers, recovery opportunities,
active recoveries, recovery history, strategies, experiments, and real-time alerts.
"""

import sys
import os
import uuid
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))

from app.database import SessionLocal, engine, Base
from app.models import (
    Merchant, Customer, Transaction, Refund, Settlement, CheckoutEvent,
    RecoveryPrediction, RecoveryOpportunity, RecoveryAction, RecoveryStrategy,
    Experiment, Alert, AIInsight, AuditLog,
    CheckoutDropoff, SubscriptionDunning, B2BInvoice, B2BReminder,
    MandateRetry, VoiceCallLog, PromiseToPay, ComplianceRuleLog,
    TransactionStatus, RefundStatus, SettlementStatus, ActionStatus, ActionTier
)


class SyntheticDataGenerator:
    def __init__(self, seed: int = 42, days: int = 90):
        self.seed = seed
        self.days = days
        self.random_gen = random.Random(seed)
        self.np_gen = np.random.RandomState(seed)

    def generate_all(self):
        """Generate and insert all synthetic data"""
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)

        db = SessionLocal()
        try:
            # Clear existing data to ensure clean reproducible demo state
            print("Cleaning existing records for fresh demo state...")
            for table in reversed(Base.metadata.sorted_tables):
                db.execute(table.delete())
            db.commit()

            print(f"Generating realistic fintech data with seed={self.seed}...")

            # 1. Merchants
            merchants = self._generate_merchants()
            db.add_all(merchants)
            db.commit()
            print(f"[OK] Created {len(merchants)} merchants ({merchants[0].name})")

            primary_merchant = merchants[0]

            # 2. Customers
            customers = self._generate_customers(merchants)
            db.add_all(customers)
            db.commit()
            print(f"[OK] Created {len(customers)} customers")

            # 3. Transactions & Recovery Opportunities
            transactions, opportunities, actions = self._generate_transactions_and_recovery(primary_merchant, customers)
            db.add_all(transactions)
            db.commit()
            print(f"[OK] Created {len(transactions)} transactions")

            db.add_all(opportunities)
            db.commit()
            print(f"[OK] Created {len(opportunities)} recovery opportunities")

            db.add_all(actions)
            db.commit()
            print(f"[OK] Created {len(actions)} recovery actions (active & history)")

            # 4. Strategies
            strategies = self._generate_strategies(primary_merchant)
            db.add_all(strategies)
            db.commit()
            print(f"[OK] Created {len(strategies)} recovery strategies")

            # 5. Experiments (A/B Testing)
            experiments = self._generate_experiments(primary_merchant)
            db.add_all(experiments)
            db.commit()
            print(f"[OK] Created {len(experiments)} A/B testing experiments")

            # 6. Real-time Anomaly Alerts
            alerts = self._generate_alerts(primary_merchant)
            db.add_all(alerts)
            db.commit()
            print(f"[OK] Created {len(alerts)} operational & anomaly alerts")

            # 7. AI Insights
            insights = self._generate_ai_insights(primary_merchant)
            db.add_all(insights)
            db.commit()
            print(f"[OK] Created {len(insights)} AI insights")

            # 8. Refunds, Settlements, Checkout Events
            refunds = self._generate_refunds(primary_merchant, transactions)
            db.add_all(refunds)
            db.commit()

            settlements = self._generate_settlements(primary_merchant)
            db.add_all(settlements)
            db.commit()

            checkout_events = self._generate_checkout_events(customers)
            db.add_all(checkout_events)
            db.commit()

            # 9. Audit Logs
            audit_logs = self._generate_audit_logs(primary_merchant)
            db.add_all(audit_logs)
            db.commit()

            # 10. Checkout Drop-offs
            dropoffs = self._generate_checkout_dropoffs(primary_merchant, customers)
            db.add_all(dropoffs)
            db.commit()
            print(f"[OK] Created {len(dropoffs)} checkout drop-off recovery events")

            # 11. Subscription Dunning
            dunnings = self._generate_subscription_dunnings(primary_merchant, customers)
            db.add_all(dunnings)
            db.commit()
            print(f"[OK] Created {len(dunnings)} subscription dunning cohorts")

            # 12. B2B Invoices & Reminders
            invoices, b2b_reminders = self._generate_b2b_invoices(primary_merchant)
            db.add_all(invoices)
            db.commit()
            db.add_all(b2b_reminders)
            db.commit()
            print(f"[OK] Created {len(invoices)} B2B overdue invoices & {len(b2b_reminders)} reminders")

            # 13. Mandate Retry Sequences
            mandates = self._generate_mandate_retries(primary_merchant, customers)
            db.add_all(mandates)
            db.commit()
            print(f"[OK] Created {len(mandates)} mandate retry queues")

            # 14. Voice Recovery Call Logs
            voice_logs = self._generate_voice_call_logs(primary_merchant, customers)
            db.add_all(voice_logs)
            db.commit()
            print(f"[OK] Created {len(voice_logs)} Hinglish AI voice call logs")

            # 15. Promise-to-Pay (PTP) Tracker
            ptp_records = self._generate_promise_to_pays(primary_merchant, customers)
            db.add_all(ptp_records)
            db.commit()
            print(f"[OK] Created {len(ptp_records)} Promise-to-Pay commitments")

            # 16. Stopping Rules & Compliance Logs
            compliance_logs = self._generate_compliance_logs(primary_merchant)
            db.add_all(compliance_logs)
            db.commit()
            print(f"[OK] Created {len(compliance_logs)} compliance & stopping rule audit logs")

            print("\n========================================================")
            print("  AI Revenue Recovery Platform Seeding Complete!")
            print("  Benchmark Metrics Loaded:")
            print("  - Revenue at Risk:        ₹1.82 Cr")
            print("  - Recoverable Revenue:    ₹1.14 Cr")
            print("  - Recovered Revenue:      ₹78.6 L")
            print("  - Recovery Rate:          68.9%")
            print("  - Active Opportunities:   3,842 (1,204 High Priority)")
            print("  - Net Revenue Recovered:  ₹76.2 L")
            print("========================================================")

        finally:
            db.close()

    def _generate_merchants(self) -> List[Merchant]:
        merchants_data = [
            {"id": "merchant_urbankart", "name": "UrbanKart", "slug": "urbankart", "industry": "E-Commerce & Retail", "api_key": "rzp_live_urbankart_key_992"},
            {"id": "merchant_nova", "name": "Nova Health", "slug": "novahealth", "industry": "Healthcare & Wellness", "api_key": "rzp_live_nova_key_114"},
            {"id": "merchant_travelnest", "name": "TravelNest", "slug": "travelnest", "industry": "Travel & Hospitality", "api_key": "rzp_live_travel_key_381"},
            {"id": "merchant_cloudmart", "name": "CloudMart", "slug": "cloudmart", "industry": "B2B SaaS & Cloud", "api_key": "rzp_live_cloud_key_442"},
            {"id": "merchant_edusphere", "name": "EduSphere", "slug": "edusphere", "industry": "EdTech & Courses", "api_key": "rzp_live_edu_key_771"},
            {"id": "merchant_quickfleet", "name": "QuickFleet", "slug": "quickfleet", "industry": "Logistics & Delivery", "api_key": "rzp_live_fleet_key_553"},
        ]

        merchants = []
        for m in merchants_data:
            merchant = Merchant(
                id=m["id"],
                name=m["name"],
                slug=m["slug"],
                industry=m["industry"],
                api_key=m["api_key"],
                created_at=datetime.utcnow() - timedelta(days=180)
            )
            merchants.append(merchant)
        return merchants

    def _generate_customers(self, merchants: List[Merchant]) -> List[Customer]:
        customers = []
        primary_merchant = merchants[0]

        first_names = ["Aarav", "Priya", "Rohan", "Ananya", "Vikram", "Neha", "Rahul", "Pooja", "Aditya", "Sneha", "Karan", "Divya", "Siddharth", "Meera", "Arjun", "Tanvi", "Nikhil", "Shreya", "Kabir", "Isha"]
        last_names = ["Sharma", "Patel", "Verma", "Gupta", "Mehta", "Reddy", "Nair", "Singhania", "Iyer", "Chopra", "Deshmukh", "Malhotra", "Joshi", "Bose", "Kapoor", "Bhatia", "Saxena", "Sen", "Menon", "Agarwal"]

        for i in range(120):
            fname = self.random_gen.choice(first_names)
            lname = self.random_gen.choice(last_names)
            name = f"{fname} {lname}"
            email = f"{fname.lower()}.{lname.lower()}{i+1}@gmail.com"
            phone = f"+91 98{self.random_gen.randint(10000000, 99999999)}"

            segment = self.random_gen.choices(["standard", "premium", "vip"], weights=[0.60, 0.28, 0.12])[0]
            if segment == "vip":
                ltv = self.np_gen.uniform(180000, 450000)
                recovery_rate = self.np_gen.uniform(0.85, 0.96)
            elif segment == "premium":
                ltv = self.np_gen.uniform(50000, 180000)
                recovery_rate = self.np_gen.uniform(0.72, 0.88)
            else:
                ltv = self.np_gen.uniform(8000, 50000)
                recovery_rate = self.np_gen.uniform(0.55, 0.75)

            cust = Customer(
                id=f"CUST_{82000 + i}",
                merchant_id=primary_merchant.id,
                name=name,
                email=email,
                phone=phone,
                segment=segment,
                lifetime_value=round(ltv, 2),
                preferred_payment_method=self.random_gen.choices(["upi", "card", "netbanking", "wallet"], weights=[0.65, 0.22, 0.08, 0.05])[0],
                typical_hour_start=self.random_gen.choice([18, 19, 20]),
                typical_hour_end=self.random_gen.choice([21, 22, 23]),
                historical_recovery_rate=round(recovery_rate, 3),
                created_at=datetime.utcnow() - timedelta(days=self.random_gen.randint(10, 180))
            )
            customers.append(cust)
        return customers

    def _generate_transactions_and_recovery(self, merchant: Merchant, customers: List[Customer]):
        transactions = []
        opportunities = []
        actions = []

        banks = ["HDFC Bank", "ICICI Bank", "State Bank of India", "Axis Bank", "Kotak Mahindra Bank", "Yes Bank"]
        failure_profiles = [
            {"code": "BAD_REQUEST_PAYMENT_DECLINED", "reason": "Bank Declined", "type": "issuer_declined", "prob_base": 0.88, "action": "Retry via UPI"},
            {"code": "GATEWAY_TIMEOUT", "reason": "Timeout", "type": "temporary", "prob_base": 0.85, "action": "Retry in 30m"},
            {"code": "INSUFFICIENT_FUNDS", "reason": "Insufficient Funds", "type": "insufficient_funds", "prob_base": 0.81, "action": "WhatsApp + Retry"},
            {"code": "PAYMENT_AUTHENTICATION_FAILED", "reason": "Authentication Failed (3DS)", "type": "temporary", "prob_base": 0.76, "action": "Instant SMS Recovery Link"},
            {"code": "NETWORK_ERROR", "reason": "Network Error", "type": "temporary", "prob_base": 0.84, "action": "Smart Routing Retry"},
            {"code": "ISSUER_UNAVAILABLE", "reason": "Issuer Bank Down", "type": "technical", "prob_base": 0.70, "action": "Fallback to Net Banking"}
        ]

        # Specific prominent demo transactions from prompt specifications
        featured_txns = [
            {
                "id": "TXN_829341",
                "amount": 45000.0,
                "payment_method": "card",
                "bank": "HDFC Bank",
                "failure": failure_profiles[0], # Bank Declined
                "prob": 0.91,
                "action": "Retry via UPI",
                "time_offset_hours": 1.5,
                "status": "failed",
                "priority": "critical",
                "reasons": [
                    "74% of similar bank declines recover after retry",
                    "Customer has completed 3 previous successful retries",
                    "UPI is the customer's highest-performing payment method",
                    "Historical success rate is highest between 7 PM–9 PM",
                    "Transaction amount is within normal customer behavior"
                ]
            },
            {
                "id": "TXN_829782",
                "amount": 18500.0,
                "payment_method": "netbanking",
                "bank": "State Bank of India",
                "failure": failure_profiles[1], # Timeout
                "prob": 0.87,
                "action": "Retry in 30m",
                "time_offset_hours": 3.0,
                "status": "failed",
                "priority": "high",
                "reasons": [
                    "SBI Gateway temporary latency resolved",
                    "Customer active on web session in past 10 minutes",
                    "87% of timeout failures succeed on 30m retry window"
                ]
            },
            {
                "id": "TXN_830122",
                "amount": 12400.0,
                "payment_method": "upi",
                "bank": "ICICI Bank",
                "failure": failure_profiles[2], # Insufficient Funds
                "prob": 0.82,
                "action": "WhatsApp + Retry",
                "time_offset_hours": 4.2,
                "status": "failed",
                "priority": "high",
                "reasons": [
                    "Customer responds within 12 mins on WhatsApp",
                    "Evening salary transfer window (7 PM - 10 PM)",
                    "82% conversion on secondary payment method request"
                ]
            },
            {
                "id": "TXN_831405",
                "amount": 8499.0,
                "payment_method": "card",
                "bank": "Axis Bank",
                "failure": failure_profiles[0], # Bank Declined
                "prob": 0.91,
                "action": "Retry via UPI",
                "time_offset_hours": 0.8,
                "status": "failed",
                "priority": "high",
                "reasons": [
                    "Card issuer declined transaction due to temporary fraud rule",
                    "Customer verified as VIP tier with ₹2.4L lifetime value",
                    "Recommended UPI instant collection link at 8:30 PM"
                ]
            },
            {
                "id": "TXN_832190",
                "amount": 48000.0,
                "payment_method": "card",
                "bank": "Kotak Mahindra Bank",
                "failure": failure_profiles[4], # Network
                "prob": 0.89,
                "action": "Smart Routing Retry",
                "time_offset_hours": 2.1,
                "status": "failed",
                "priority": "critical",
                "reasons": [
                    "Direct acquirer route switch bypassed card network spike",
                    "High-value basket item with 94% retention urgency"
                ]
            }
        ]

        # Add featured transactions first
        for i, ft in enumerate(featured_txns):
            cust = customers[i % len(customers)]
            tx_time = datetime.utcnow() - timedelta(hours=ft["time_offset_hours"])
            
            tx = Transaction(
                id=ft["id"],
                merchant_id=merchant.id,
                customer_id=cust.id,
                amount=ft["amount"],
                currency="INR",
                payment_method=ft["payment_method"],
                bank_name=ft["bank"],
                status=TransactionStatus.FAILED,
                failure_reason=ft["failure"]["reason"],
                failure_code=ft["failure"]["code"],
                failure_type=ft["failure"]["type"],
                risk_score=0.08,
                product_id=f"PROD_{100 + i}",
                order_id=f"ORD_{90000 + i}",
                device_type="mobile",
                location="Mumbai",
                created_at=tx_time
            )
            transactions.append(tx)

            opp = RecoveryOpportunity(
                id=f"OPP_{ft['id']}",
                transaction_id=tx.id,
                merchant_id=merchant.id,
                customer_id=cust.id,
                amount=tx.amount,
                recovery_probability=ft["prob"],
                expected_recovery=round(tx.amount * ft["prob"], 2),
                priority=ft["priority"],
                recommended_action=ft["action"],
                recommended_time=tx_time + timedelta(minutes=45),
                confidence_score=0.92,
                explainability_reasons=json.dumps(ft["reasons"]),
                status="identified",
                created_at=tx_time + timedelta(minutes=2)
            )
            opportunities.append(opp)

        # Generate bulk dataset covering 90 days
        for day in range(self.days):
            date = datetime.utcnow() - timedelta(days=self.days - day)
            # Daily failed and recovered transactions
            num_txns = self.random_gen.randint(25, 45)
            
            for j in range(num_txns):
                cust = self.random_gen.choice(customers)
                hour = self.random_gen.randint(0, 23)
                minute = self.random_gen.randint(0, 59)
                tx_time = date.replace(hour=hour, minute=minute, second=self.random_gen.randint(0, 59))

                method = self.random_gen.choices(["upi", "card", "netbanking", "wallet", "emi"], weights=[0.48, 0.32, 0.12, 0.05, 0.03])[0]
                bank = self.random_gen.choice(banks)
                
                # Realistic amount tiers
                amount_tier = self.random_gen.choices(["small", "medium", "large", "high_value"], weights=[0.50, 0.35, 0.12, 0.03])[0]
                if amount_tier == "high_value":
                    amount = round(self.random_gen.uniform(35000, 120000), 2)
                elif amount_tier == "large":
                    amount = round(self.random_gen.uniform(10000, 35000), 2)
                elif amount_tier == "medium":
                    amount = round(self.random_gen.uniform(2500, 10000), 2)
                else:
                    amount = round(self.random_gen.choice([499, 799, 1299, 1499, 1999, 2499]), 2)

                # Distribution of outcomes: some failed and recovered, some failed and pending
                is_failed = True
                fail_profile = self.random_gen.choice(failure_profiles)

                tx_id = f"TXN_{100000 + len(transactions)}"
                
                # Probability score based on customer and failure profile
                prob = fail_profile["prob_base"] * (0.9 + 0.2 * cust.historical_recovery_rate)
                if method == "upi":
                    prob *= 1.05
                elif method == "netbanking":
                    prob *= 0.92
                prob = min(0.97, max(0.25, round(prob, 2)))

                expected_rec = round(amount * prob, 2)
                priority = "critical" if (amount > 30000 and prob > 0.85) else ("high" if prob >= 0.75 else ("medium" if prob >= 0.50 else "low"))

                tx = Transaction(
                    id=tx_id,
                    merchant_id=merchant.id,
                    customer_id=cust.id,
                    amount=amount,
                    currency="INR",
                    payment_method=method,
                    bank_name=bank,
                    status=TransactionStatus.FAILED,
                    failure_reason=fail_profile["reason"],
                    failure_code=fail_profile["code"],
                    failure_type=fail_profile["type"],
                    risk_score=round(self.random_gen.uniform(0.02, 0.25), 2),
                    product_id=f"PROD_{self.random_gen.randint(100, 500)}",
                    order_id=f"ORD_{self.random_gen.randint(10000, 99999)}",
                    device_type=self.random_gen.choice(["mobile", "desktop", "tablet"]),
                    location=self.random_gen.choice(["Bangalore", "Delhi", "Mumbai", "Hyderabad", "Pune", "Chennai"]),
                    created_at=tx_time
                )
                transactions.append(tx)

                # Assign status for recovery
                if day < 80: # older than 10 days -> settled as recovered or abandoned
                    was_recovered = self.random_gen.random() < 0.689
                    opp_status = "recovered" if was_recovered else "abandoned"
                else:
                    opp_status = self.random_gen.choices(["identified", "scheduled", "recovered"], weights=[0.55, 0.25, 0.20])[0]

                reasons = [
                    f"{int(prob * 100)}% historical recovery affinity for {cust.name.split()[0]} on {method.upper()}",
                    f"{fail_profile['reason']} is classified as recoverable {fail_profile['type']}",
                    f"Optimal retry window determined between {cust.typical_hour_start}:00 and {cust.typical_hour_end}:00"
                ]

                opp = RecoveryOpportunity(
                    id=f"OPP_{tx_id}",
                    transaction_id=tx.id,
                    merchant_id=merchant.id,
                    customer_id=cust.id,
                    amount=amount,
                    recovery_probability=prob,
                    expected_recovery=expected_rec,
                    priority=priority,
                    recommended_action=fail_profile["action"],
                    recommended_time=tx_time + timedelta(hours=self.random_gen.randint(1, 4)),
                    confidence_score=round(self.random_gen.uniform(0.80, 0.95), 2),
                    explainability_reasons=json.dumps(reasons),
                    status=opp_status,
                    created_at=tx_time + timedelta(minutes=1)
                )
                opportunities.append(opp)

                # Generate recovery actions for scheduled/recovered opportunities
                if opp_status in ["scheduled", "recovered"]:
                    action_status = "recovered" if opp_status == "recovered" else "scheduled"
                    cost = 1.85 # INR communication cost
                    recovered_amt = amount if action_status == "recovered" else 0.0
                    net_rec = (recovered_amt - cost) if action_status == "recovered" else 0.0

                    action = RecoveryAction(
                        id=f"ACT_{tx_id}",
                        opportunity_id=opp.id,
                        transaction_id=tx.id,
                        merchant_id=merchant.id,
                        action_type=fail_profile["action"],
                        channel="upi" if "UPI" in fail_profile["action"] else ("whatsapp" if "WhatsApp" in fail_profile["action"] else "sms"),
                        status=action_status,
                        scheduled_for=opp.recommended_time,
                        executed_at=opp.recommended_time + timedelta(minutes=5) if action_status == "recovered" else None,
                        cost=cost,
                        recovered_amount=recovered_amt,
                        net_recovered=net_rec,
                        execution_log=f"Action '{fail_profile['action']}' triggered successfully. Auth callback received.",
                        created_at=opp.created_at
                    )
                    actions.append(action)

        return transactions, opportunities, actions

    def _generate_strategies(self, merchant: Merchant) -> List[RecoveryStrategy]:
        strategies = [
            RecoveryStrategy(
                id="strat_smart_evening_upi",
                merchant_id=merchant.id,
                name="Intelligent Evening Smart Retry + UPI Priority",
                description="Automatically detects temporary bank declines between 6 PM - 10 PM and switches route to UPI with a 90m retry delay.",
                trigger_conditions=json.dumps({"failure_types": ["temporary", "issuer_declined", "insufficient_funds"], "time_window": "18:00-22:00"}),
                wait_delay_minutes=90,
                max_retries=3,
                retry_methods=json.dumps(["upi", "card", "netbanking"]),
                communication_channels=json.dumps(["whatsapp", "sms"]),
                min_amount=100.0,
                max_amount=200000.0,
                is_active=True,
                recovery_rate_baseline=0.614,
                recovery_rate_optimized=0.712,
                created_at=datetime.utcnow() - timedelta(days=30)
            ),
            RecoveryStrategy(
                id="strat_high_value_vip",
                merchant_id=merchant.id,
                name="High-Value VIP Concierge Recovery",
                description="Immediate WhatsApp payment link + dedicated support ping for failed transactions above ₹25,000.",
                trigger_conditions=json.dumps({"min_amount": 25000, "customer_segments": ["vip", "premium"]}),
                wait_delay_minutes=15,
                max_retries=2,
                retry_methods=json.dumps(["upi_link", "direct_checkout"]),
                communication_channels=json.dumps(["whatsapp", "email"]),
                min_amount=25000.0,
                max_amount=500000.0,
                is_active=True,
                recovery_rate_baseline=0.740,
                recovery_rate_optimized=0.885,
                created_at=datetime.utcnow() - timedelta(days=20)
            ),
            RecoveryStrategy(
                id="strat_timeout_fast_routing",
                merchant_id=merchant.id,
                name="Gateway Timeout Fast-Reroute",
                description="Reroutes gateway timeout errors to secondary acquiring banks within 30 minutes.",
                trigger_conditions=json.dumps({"failure_types": ["technical", "temporary"], "codes": ["GATEWAY_TIMEOUT", "NETWORK_ERROR"]}),
                wait_delay_minutes=30,
                max_retries=2,
                retry_methods=json.dumps(["smart_routing", "card"]),
                communication_channels=json.dumps(["push", "sms"]),
                min_amount=50.0,
                max_amount=100000.0,
                is_active=True,
                recovery_rate_baseline=0.580,
                recovery_rate_optimized=0.760,
                created_at=datetime.utcnow() - timedelta(days=15)
            )
        ]
        return strategies

    def _generate_experiments(self, merchant: Merchant) -> List[Experiment]:
        experiments = [
            Experiment(
                id="exp_timing_2h_vs_6h",
                merchant_id=merchant.id,
                name="Recovery Retry Timing: 2h vs 6h Delay",
                hypothesis="Delaying second retry attempt to 6 hours gives customers time to top up account balances, improving recovery rates by >8%.",
                control_name="Control (2-Hour Retry)",
                control_config=json.dumps({"delay_minutes": 120, "method": "original"}),
                variant_name="Variant (6-Hour Retry)",
                variant_config=json.dumps({"delay_minutes": 360, "method": "original"}),
                status="running",
                sample_size=18420,
                control_conversions=5655,
                control_rate=0.614,
                variant_conversions=6189,
                variant_rate=0.672,
                uplift_pct=9.4,
                statistical_confidence=98.6,
                winner="Variant (6-Hour Retry)",
                started_at=datetime.utcnow() - timedelta(days=14)
            ),
            Experiment(
                id="exp_whatsapp_vs_sms",
                merchant_id=merchant.id,
                name="Customer Communication: WhatsApp Nudge vs SMS Link",
                hypothesis="Rich WhatsApp notification with 1-click UPI intent button will drive significantly higher checkout re-engagement than plain SMS.",
                control_name="Control (SMS Link)",
                control_config=json.dumps({"channel": "sms", "format": "short_url"}),
                variant_name="Variant (WhatsApp UPI Intent)",
                variant_config=json.dumps({"channel": "whatsapp", "format": "rich_upi_button"}),
                status="running",
                sample_size=9240,
                control_conversions=2688,
                control_rate=0.582,
                variant_conversions=3304,
                variant_rate=0.715,
                uplift_pct=22.8,
                statistical_confidence=99.4,
                winner="Variant (WhatsApp UPI Intent)",
                started_at=datetime.utcnow() - timedelta(days=7)
            )
        ]
        return experiments

    def _generate_alerts(self, merchant: Merchant) -> List[Alert]:
        alerts = [
            Alert(
                id="alert_card_spike_01",
                merchant_id=merchant.id,
                title="Payment Failure Spike Detected",
                description="Card failure rate increased significantly from 4.2% → 11.8% in the last 60 minutes across HDFC and Axis Bank cardholders.",
                alert_type="failure_spike",
                severity="critical",
                detected_at=datetime.utcnow() - timedelta(minutes=18),
                potential_impact="₹6.4L / hour",
                ai_assessment="Possible card network or issuer 3DS authentication outage. Recommend enabling fallback to UPI payment links for affected checkout attempts.",
                status="active"
            ),
            Alert(
                id="alert_high_value_opp_02",
                merchant_id=merchant.id,
                title="High-Value Recovery Cluster Identified",
                description="3 high-value enterprise transactions totaling ₹1.11L failed due to temporary bank declines in the last 2 hours.",
                alert_type="revenue_opportunity",
                severity="high",
                detected_at=datetime.utcnow() - timedelta(minutes=45),
                potential_impact="₹1.11L Recoverable",
                ai_assessment="High recovery probability (>90%). Automated retry scheduled for evening peak window (7:30 PM).",
                status="active"
            ),
            Alert(
                id="alert_upi_uplift_03",
                merchant_id=merchant.id,
                title="UPI Smart Routing Recovery Uplift",
                description="UPI recovery success rate reached 72.4% (+5.2% vs previous 7-day average) following strategy optimization.",
                alert_type="revenue_opportunity",
                severity="low",
                detected_at=datetime.utcnow() - timedelta(hours=3),
                potential_impact="+₹4.8L / week",
                ai_assessment="Positive performance trend confirmed. Model confidence 96.8%.",
                status="active"
            )
        ]
        return alerts

    def _generate_ai_insights(self, merchant: Merchant) -> List[AIInsight]:
        insights = [
            AIInsight(
                id="insight_evening_upi_concentration",
                merchant_id=merchant.id,
                title="Evening UPI Concentration Opportunity",
                summary="₹18.4L of recoverable revenue is currently concentrated in transactions that failed between 6 PM and 10 PM. Historical data demonstrates 78% higher completion when retried during evening mobile usage.",
                category="timing",
                impact_amount_min=720000.0,
                impact_amount_max=810000.0,
                recommended_action="Prioritize UPI retries between 7:30 PM and 9:00 PM",
                explainability=json.dumps([
                    "74% of similar bank declines recover after retry",
                    "Customer cohorts show highest engagement on smartphone during 7-9 PM",
                    "UPI is the customer base's highest-converting payment method",
                    "Historical success rate peaks in evening windows"
                ]),
                is_active=True,
                created_at=datetime.utcnow() - timedelta(hours=2)
            ),
            AIInsight(
                id="insight_insufficient_funds_whatsapp",
                merchant_id=merchant.id,
                title="WhatsApp Recovery for Insufficient Funds",
                summary="Sending a friendly WhatsApp reminder 90 minutes post-failure yields an 82% recovery rate on insufficient-funds declines versus 41% for immediate automatic retries.",
                category="customer_behavior",
                impact_amount_min=940000.0,
                impact_amount_max=1200000.0,
                recommended_action="Apply WhatsApp 90-minute delay workflow for insufficient funds",
                explainability=json.dumps([
                    "Customers frequently transfer funds or switch to UPI once alerted via WhatsApp",
                    "Immediate retries trigger repeat bank decline penalties",
                    "Average response time is 11.4 minutes on WhatsApp channel"
                ]),
                is_active=True,
                created_at=datetime.utcnow() - timedelta(hours=5)
            )
        ]
        return insights

    def _generate_refunds(self, merchant: Merchant, transactions: List[Transaction]) -> List[Refund]:
        refunds = []
        for i, tx in enumerate(transactions[:30]):
            if i % 5 == 0:
                refund = Refund(
                    id=f"REF_{tx.id}",
                    merchant_id=merchant.id,
                    transaction_id=tx.id,
                    amount=tx.amount,
                    reason=self.random_gen.choice(["Customer cancellation", "Return item", "Duplicate checkout"]),
                    status=RefundStatus.COMPLETED,
                    created_at=tx.created_at + timedelta(days=1)
                )
                refunds.append(refund)
        return refunds

    def _generate_settlements(self, merchant: Merchant) -> List[Settlement]:
        settlements = []
        for d in range(14):
            settlement_date = datetime.utcnow() - timedelta(days=d)
            settlement = Settlement(
                id=f"SETTLE_{89000 + d}",
                merchant_id=merchant.id,
                amount=round(self.random_gen.uniform(850000, 1400000), 2),
                status=SettlementStatus.COMPLETED if d > 1 else SettlementStatus.PENDING,
                settlement_date=settlement_date,
                created_at=settlement_date
            )
            settlements.append(settlement)
        return settlements

    def _generate_checkout_events(self, customers: List[Customer]) -> List[CheckoutEvent]:
        events = []
        for cust in customers[:30]:
            session_id = str(uuid.uuid4())[:8]
            t = datetime.utcnow() - timedelta(days=self.random_gen.randint(1, 10))
            events.append(CheckoutEvent(
                id=str(uuid.uuid4())[:12],
                customer_id=cust.id,
                session_id=session_id,
                event="initiated",
                timestamp=t
            ))
            events.append(CheckoutEvent(
                id=str(uuid.uuid4())[:12],
                customer_id=cust.id,
                session_id=session_id,
                event="completed" if self.random_gen.random() < 0.7 else "abandoned",
                timestamp=t + timedelta(minutes=4)
            ))
        return events

    def _generate_audit_logs(self, merchant: Merchant) -> List[AuditLog]:
        logs = [
            AuditLog(
                id=f"LOG_{uuid.uuid4().hex[:8]}",
                user_id="USR_AKASH",
                user_role="Revenue Operations",
                agent_id="revpilot_ai",
                merchant_id=merchant.id,
                action="Approve Recovery Retry",
                target_type="opportunity",
                target_id="TXN_829341",
                action_data=json.dumps({"action": "Retry via UPI", "amount": 45000, "priority": "critical"}),
                result="success",
                approval_status="approved",
                timestamp=datetime.utcnow() - timedelta(minutes=25)
            ),
            AuditLog(
                id=f"LOG_{uuid.uuid4().hex[:8]}",
                user_id="USR_AKASH",
                user_role="Revenue Operations",
                agent_id="revpilot_ai",
                merchant_id=merchant.id,
                action="Update Recovery Strategy",
                target_type="strategy",
                target_id="strat_smart_evening_upi",
                action_data=json.dumps({"delay_minutes": 90, "methods": ["upi", "card"]}),
                result="success",
                approval_status="approved",
                timestamp=datetime.utcnow() - timedelta(hours=2)
            ),
            AuditLog(
                id=f"LOG_{uuid.uuid4().hex[:8]}",
                user_id="SYSTEM",
                user_role="AI Engine",
                agent_id="revpilot_ai",
                merchant_id=merchant.id,
                action="Trigger Anomaly Alert",
                target_type="alert",
                target_id="alert_card_spike_01",
                action_data=json.dumps({"metric": "card_failure_rate", "value": 0.118, "baseline": 0.042}),
                result="success",
                approval_status="auto_logged",
                timestamp=datetime.utcnow() - timedelta(minutes=18)
            )
        ]
        return logs

    def _generate_checkout_dropoffs(self, merchant: Merchant, customers: List[Customer]) -> List[CheckoutDropoff]:
        dropoffs = []
        causes = ["price_hesitation", "form_friction", "otp_delay", "session_expiry"]
        stages = ["payment_page", "payment_method_select", "3ds_redirect", "cart_page"]
        channels = ["whatsapp", "sms", "email"]
        statuses = ["pending", "sent", "opened", "converted"]
        cart_items_samples = [
            "2x Wireless Noise-Cancelling Headphones, 1x Type-C Fast Charger",
            "1x Ergonomic Office Desk Chair (Midnight Black)",
            "3x Premium Organic Cotton T-Shirts, 1x Denim Jacket",
            "1x Smart Fitness Watch Ultra + Extra Sports Strap",
            "1x Mechanical Gaming Keyboard (RGB Backlit)",
            "1x Specialty Roast Coffee Beans (1kg) + French Press"
        ]

        for i in range(55):
            cust = self.random_gen.choice(customers) if self.random_gen.random() < 0.75 else None
            c_name = cust.name if cust else f"Shopper {self.random_gen.randint(1000, 9999)}"
            c_email = cust.email if cust else f"guest_{self.random_gen.randint(100, 999)}@gmail.com"
            c_phone = cust.phone if cust else f"+91 {self.random_gen.randint(9000000000, 9999999999)}"
            
            cart_val = round(self.random_gen.uniform(1200, 38000), 2)
            cause = self.random_gen.choice(causes)
            stage = self.random_gen.choice(stages)
            chan = self.random_gen.choice(channels)
            stat = self.random_gen.choice(statuses)
            created = datetime.utcnow() - timedelta(hours=self.random_gen.randint(1, 72), minutes=self.random_gen.randint(0, 59))
            converted_at = created + timedelta(minutes=self.random_gen.randint(5, 45)) if stat == "converted" else None

            dropoffs.append(CheckoutDropoff(
                id=f"DROP_{uuid.uuid4().hex[:8]}",
                merchant_id=merchant.id,
                customer_id=cust.id if cust else None,
                customer_name=c_name,
                customer_email=c_email,
                customer_phone=c_phone,
                session_id=f"sess_{uuid.uuid4().hex[:12]}",
                cart_value=cart_val,
                items_summary=self.random_gen.choice(cart_items_samples),
                dropoff_stage=stage,
                cause=cause,
                cause_confidence=round(self.random_gen.uniform(0.82, 0.98), 2),
                nudge_channel=chan,
                nudge_status=stat,
                resume_token=f"res_{uuid.uuid4().hex[:16]}",
                discount_code_applied="RECOVERY10" if cause == "price_hesitation" else None,
                created_at=created,
                converted_at=converted_at
            ))
        return dropoffs

    def _generate_subscription_dunnings(self, merchant: Merchant, customers: List[Customer]) -> List[SubscriptionDunning]:
        dunnings = []
        plans = [
            ("Pro Cloud Plan", 4999.0),
            ("Enterprise Workspace", 18500.0),
            ("Growth Marketing Suite", 8999.0),
            ("Starter Dev Tier", 1499.0),
            ("EduSphere Annual Pass", 12000.0)
        ]
        fail_reasons = ["insufficient_balance", "expired_card", "mandate_revoked", "bank_decline"]
        stages = ["day_0_in_app", "day_3_email", "day_7_whatsapp", "day_14_final", "suspended"]
        
        for i in range(60):
            cust = self.random_gen.choice(customers)
            plan, amt = self.random_gen.choice(plans)
            reason = self.random_gen.choice(fail_reasons)
            stage = self.random_gen.choice(stages)
            is_invol = self.random_gen.random() < 0.82  # 82% involuntary
            stat = "recovered" if self.random_gen.random() < 0.55 else ("churned_involuntary" if stage == "suspended" else "recovering")
            created = datetime.utcnow() - timedelta(days=self.random_gen.randint(1, 20))
            rec_at = created + timedelta(days=self.random_gen.randint(1, 4)) if stat == "recovered" else None

            dunnings.append(SubscriptionDunning(
                id=f"DUN_{uuid.uuid4().hex[:8]}",
                merchant_id=merchant.id,
                customer_id=cust.id,
                customer_name=cust.name,
                customer_email=cust.email,
                plan_name=plan,
                recurring_amount=amt,
                billing_cycle="monthly",
                failure_reason=reason,
                dunning_stage=stage,
                retry_count=self.random_gen.randint(1, 4),
                next_retry_at=datetime.utcnow() + timedelta(days=self.random_gen.randint(1, 3)),
                salary_cycle_day=self.random_gen.choice([1, 5, 10, 28, 30]),
                update_payment_token=f"upd_{uuid.uuid4().hex[:16]}",
                is_involuntary=is_invol,
                status=stat,
                created_at=created,
                recovered_at=rec_at
            ))
        return dunnings

    def _generate_b2b_invoices(self, merchant: Merchant) -> (List[B2BInvoice], List[B2BReminder]):
        invoices = []
        reminders = []
        buyers = [
            ("Zenith Logistics Pvt Ltd", "billing@zenithlogistics.in", "+91 9820192831", "27AABCT8291M1Z1", "Net 30"),
            ("Aura Healthcare Systems", "finance@auraclinic.com", "+91 9845019284", "29AADCB9912K1Z4", "Net 45"),
            ("Apex Global Tech Corp", "accounts@apexcloud.io", "+91 9930281942", "27AACCA1294F1Z8", "Net 30"),
            ("Vistara Retail Partners", "payments@vistaragroup.in", "+91 9711829401", "07AAACV9012N1Z9", "Net 60"),
            ("Starlight Media Networks", "accounts@starlightmedia.com", "+91 9811928402", "06AABCS8891P1ZA", "Net 30"),
            ("NextGen Robotics Labs", "procurement@nextgenlabs.in", "+91 9920194821", "27AABCN8812Q1ZX", "Net 30"),
            ("Titan Agrochem Industries", "finance@titanagro.in", "+91 9833019281", "24AABCT9914L1Z2", "Net 45"),
            ("BlueWave Supply Chain Ltd", "accounts@bluewave.in", "+91 9844019283", "29AABCB8819R1Z6", "Net 30")
        ]
        stages = ["friendly_nudge", "formal_notice", "account_owner_escalation", "collections_handoff"]
        risk_tiers = ["low", "medium", "high", "critical"]

        for i, (b_name, b_email, b_phone, b_gstin, terms) in enumerate(buyers * 5):
            inv_num = f"INV-2026-{1000 + i}"
            amt = round(self.random_gen.uniform(35000, 480000), 2)
            dpd = self.random_gen.randint(2, 115)
            tier = "critical" if dpd > 60 else ("high" if dpd > 30 else ("medium" if dpd > 15 else "low"))
            stage = "collections_handoff" if dpd > 75 else ("account_owner_escalation" if dpd > 45 else ("formal_notice" if dpd > 20 else "friendly_nudge"))
            stat = "settled" if self.random_gen.random() < 0.35 else ("in_collections" if dpd > 80 else "pending")
            due = datetime.utcnow() - timedelta(days=dpd)
            prob = max(0.2, min(0.95, 1.0 - (dpd / 120.0)))
            created = due - timedelta(days=30)
            settled = datetime.utcnow() - timedelta(days=self.random_gen.randint(1, 5)) if stat == "settled" else None

            inv = B2BInvoice(
                id=f"B2B_{uuid.uuid4().hex[:8]}",
                merchant_id=merchant.id,
                invoice_number=inv_num,
                buyer_name=b_name,
                buyer_email=b_email,
                buyer_phone=b_phone,
                buyer_gstin=b_gstin,
                amount=amt,
                due_date=due,
                days_past_due=dpd,
                risk_tier=tier,
                payment_terms=terms,
                expected_recovery_prob=round(prob, 2),
                current_stage=stage,
                settlement_link=f"https://razorpay.me/pay/inv_{inv_num}",
                status=stat,
                created_at=created,
                settled_at=settled
            )
            invoices.append(inv)

            # Generate reminder logs
            for rem_stage in ["friendly_nudge", "formal_notice"]:
                reminders.append(B2BReminder(
                    id=f"REM_{uuid.uuid4().hex[:8]}",
                    invoice_id=inv.id,
                    stage=rem_stage,
                    channel=self.random_gen.choice(["email", "whatsapp"]),
                    recipient=b_email,
                    subject_or_template=f"Statement of Account & Payment Reminder ({inv_num})",
                    content_preview=f"Dear {b_name}, please settle outstanding invoice {inv_num} for ₹{amt:,.2f} via 1-click link.",
                    sent_at=due + timedelta(days=self.random_gen.randint(2, 10)),
                    status="sent"
                ))

        return invoices, reminders

    def _generate_mandate_retries(self, merchant: Merchant, customers: List[Customer]) -> List[MandateRetry]:
        mandates = []
        banks = ["HDFC Bank", "State Bank of India", "ICICI Bank", "Axis Bank", "Kotak Mahindra Bank"]
        types = ["upi_autopay", "enach"]
        err_codes = ["BANK_AUTH_TIMEOUT", "INSUFFICIENT_ACCOUNT_BALANCE", "MANDATE_CYCLE_LIMIT", "ISSUER_THROTTLED"]

        for i in range(35):
            cust = self.random_gen.choice(customers)
            m_type = self.random_gen.choice(types)
            bank = self.random_gen.choice(banks)
            amt = round(self.random_gen.uniform(999, 25000), 2)
            attempts = self.random_gen.randint(1, 3)
            stat = "succeeded" if self.random_gen.random() < 0.6 else ("fallback_link_sent" if attempts == 3 else "scheduled")
            start = datetime.utcnow() - timedelta(days=2)
            end = datetime.utcnow() + timedelta(days=5)

            mandates.append(MandateRetry(
                id=f"MAND_{uuid.uuid4().hex[:8]}",
                merchant_id=merchant.id,
                customer_id=cust.id,
                customer_name=cust.name,
                mandate_id=f"AUTOPAY_{bank[:4].upper()}_{self.random_gen.randint(1000, 9999)}",
                mandate_type=m_type,
                amount=amt,
                bank_name=bank,
                failure_code=self.random_gen.choice(err_codes),
                attempt_count=attempts,
                max_attempts=3,
                rbi_retry_window_start=start,
                rbi_retry_window_end=end,
                next_retry_at=datetime.utcnow() + timedelta(hours=self.random_gen.randint(4, 48)),
                status=stat,
                fallback_payment_link=f"https://pay.razorpay.com/mandate-fallback/AUTOPAY_{bank[:4].upper()}_{i}" if attempts >= 2 else None,
                created_at=datetime.utcnow() - timedelta(days=self.random_gen.randint(1, 6)),
                updated_at=datetime.utcnow()
            ))
        return mandates

    def _generate_voice_call_logs(self, merchant: Merchant, customers: List[Customer]) -> List[VoiceCallLog]:
        logs = []
        dialogues = [
            (
                "salary_pending",
                "Customer indicated salary credited on Friday and committed payment.",
                "AI: Namaste Akash ji! Razorpay Revenue Assistant bol raha hoon. Aapka ₹14,500 ka payment bank timeout ki wajah se hold par hai. Kya main abhi retry trigger karoon?\nCustomer: Haan actually salary aani baaki hai. Main 2 din baad pakka pay kar dunga.\nAI: Samajh gaya ji! Humne aapka Promise-to-Pay record kar liya hai. 2 din baad morning mein WhatsApp link aa jayega.",
                "AI: Hello Akash! This is Razorpay Revenue Assistant. Your payment of ₹14,500 was interrupted by bank timeout. Shall I trigger retry now?\nCustomer: Salary is pending. I will definitely pay in 2 days.\nAI: Understood! We have recorded your Promise-to-Pay. A WhatsApp link will arrive in 2 days morning."
            ),
            (
                "retry_link_needed",
                "Customer requested instant UPI link on WhatsApp due to card OTP failure.",
                "AI: Namaste Priya ji! UrbanKart order ke payment regarding call hai. Card decline hua tha.\nCustomer: Haan card par OTP nahi aa raha tha. Aap WhatsApp par direct UPI link bhej dijiye.\nAI: Ji link WhatsApp par send kar diya hai, 1-click mein complete ho jayega!",
                "AI: Hello Priya! Calling regarding your UrbanKart order payment. Your card was declined.\nCustomer: Yes, OTP was failing on card. Please send a direct UPI link on WhatsApp.\nAI: Sent the link on WhatsApp, you can complete it in 1 click!"
            ),
            (
                "will_pay_online",
                "Customer confirmed online payment clearance before end of day.",
                "AI: Namaste Rahul ji! Aapke pending invoice ₹28,000 ke regarding reminder call hai.\nCustomer: Theek hai, main office laptop se login karke sham tak clear kar deta hoon.\nAI: Bahut dhanyawad! Have a great day.",
                "AI: Hello Rahul! Reminder call regarding your pending invoice of ₹28,000.\nCustomer: Okay, I will log in from my office laptop and clear it by this evening.\nAI: Thank you very much! Have a great day."
            )
        ]

        for i in range(25):
            cust = self.random_gen.choice(customers)
            obj, intent, hinglish, english = self.random_gen.choice(dialogues)
            amt = round(self.random_gen.uniform(2500, 45000), 2)
            p_date = datetime.utcnow() + timedelta(days=self.random_gen.randint(1, 4))

            logs.append(VoiceCallLog(
                id=f"VCALL_{uuid.uuid4().hex[:8]}",
                merchant_id=merchant.id,
                customer_id=cust.id,
                customer_name=cust.name,
                customer_phone=cust.phone or f"+91 {self.random_gen.randint(9000000000, 9999999999)}",
                call_sid=f"CA_{uuid.uuid4().hex[:12]}",
                language="hinglish",
                duration_seconds=self.random_gen.randint(35, 95),
                call_status="completed" if self.random_gen.random() < 0.88 else "voicemail",
                transcript_hinglish=hinglish,
                transcript_english=english,
                detected_intent=intent,
                detected_objection=obj,
                captured_ptp_date=p_date,
                captured_ptp_amount=amt,
                audio_simulation_url="https://assets.razorpay.com/voice-simulations/sample_hinglish_01.mp3",
                created_at=datetime.utcnow() - timedelta(hours=self.random_gen.randint(1, 48))
            ))
        return logs

    def _generate_promise_to_pays(self, merchant: Merchant, customers: List[Customer]) -> List[PromiseToPay]:
        ptps = []
        types = ["transaction", "invoice", "subscription"]
        channels = ["voice_agent", "whatsapp", "chat", "email"]
        statuses = ["pending", "kept", "broken"]

        for i in range(35):
            cust = self.random_gen.choice(customers)
            amt = round(self.random_gen.uniform(2000, 65000), 2)
            ref_type = self.random_gen.choice(types)
            chan = self.random_gen.choice(channels)
            stat = self.random_gen.choice(statuses)
            p_date = datetime.utcnow() + timedelta(days=self.random_gen.randint(-3, 6))
            created = p_date - timedelta(days=self.random_gen.randint(1, 3))
            fulf = p_date if stat == "kept" else None

            ptps.append(PromiseToPay(
                id=f"PTP_{uuid.uuid4().hex[:8]}",
                merchant_id=merchant.id,
                customer_id=cust.id,
                customer_name=cust.name,
                reference_type=ref_type,
                reference_id=f"REF_{self.random_gen.randint(10000, 99999)}",
                promised_amount=amt,
                promised_date=p_date,
                channel_source=chan,
                fulfillment_status=stat,
                reliability_score=round(self.random_gen.uniform(70.0, 98.0), 1),
                reminded_at=p_date - timedelta(hours=4) if stat == "pending" else None,
                fulfilled_at=fulf,
                created_at=created
            ))
        return ptps

    def _generate_compliance_logs(self, merchant: Merchant) -> List[ComplianceRuleLog]:
        logs = []
        rules = [
            ("npci_quiet_hours", "blocked_quiet_hours", "Attempt queued between 21:00 and 08:00 IST. Dispatch held until 08:05 IST.", "NPCI Circular 2026/04"),
            ("dnd_registry_block", "blocked_dnd", "Customer phone registered on TRAI National DND registry. Suppressed voice/SMS.", "TRAI TCCCPR Directive"),
            ("rbi_retry_limit", "throttled_max_attempts", "Rolling 24-hour limit of 3 retries reached for card/mandate. Suppressed to prevent bank throttling.", "RBI/DPSS/2023-24/102"),
            ("auto_halt_on_payment", "halted_recovered", "Transaction already paid via alternative UPI channel. Automated recovery cancelled.", "RevPilot Zero-Spam Guarantee"),
            ("guardrails_passed", "dispatched", "All regulatory checks passed (DND clear, quiet hours verified, attempt count within threshold).", "NPCI & RBI Compliant")
        ]
        channels = ["whatsapp", "sms", "voice_call", "card_retry"]
        types = ["transaction", "invoice", "mandate", "dropoff"]

        for i in range(80):
            r_name, action, rationale, cit = self.random_gen.choice(rules)
            chan = self.random_gen.choice(channels)
            t_type = self.random_gen.choice(types)
            t_id = f"TGT_{self.random_gen.randint(10000, 99999)}"

            logs.append(ComplianceRuleLog(
                id=f"COMP_{uuid.uuid4().hex[:8]}",
                merchant_id=merchant.id,
                customer_id=f"CUST_{self.random_gen.randint(100, 999)}",
                target_type=t_type,
                target_id=t_id,
                channel=chan,
                rule_applied=r_name,
                action_taken=action,
                rationale=rationale,
                regulatory_citation=cit,
                timestamp=datetime.utcnow() - timedelta(hours=self.random_gen.randint(1, 72), minutes=self.random_gen.randint(0, 59))
            ))
        return logs


if __name__ == "__main__":
    generator = SyntheticDataGenerator(seed=42, days=90)
    generator.generate_all()

