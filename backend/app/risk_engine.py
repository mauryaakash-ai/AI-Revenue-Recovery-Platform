"""
Pre-Recovery Fraud & Risk Engine
Analyzes:
- Transaction velocity (1-hour and 24-hour frequency)
- Amount deviation from customer historical baseline
- Multi-instrument rapid switching
- Prior recovery attempt fatigue
- Suspicious decline codes & blacklisting
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import Transaction, Customer, RiskAssessment


class RiskTier:
    LOW_RISK = "LOW_RISK"
    MEDIUM_RISK = "MEDIUM_RISK"
    HIGH_RISK = "HIGH_RISK"
    BLOCKED = "BLOCKED"


class RiskEngine:
    """Evaluates transaction fraud risk before recovery orchestration"""

    @classmethod
    def assess_risk(
        cls,
        transaction: Dict[str, Any],
        customer: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        risk_score = 0.0
        risk_factors: List[str] = []

        amount = float(transaction.get("amount", 0.0))
        customer_id = transaction.get("customer_id")
        failure_code = transaction.get("failure_code", "")

        # 1. Hard Block Checks (Stolen, Fraud, Blacklisted)
        hard_block_keywords = ["stolen", "lost_card", "blacklisted", "fraud", "sanction"]
        if any(kw in (failure_code or "").lower() for kw in hard_block_keywords):
            risk_score = 100.0
            risk_factors.append(f"Hard block indicator in decline code: {failure_code}")
            return cls._build_result(
                risk_score=risk_score,
                risk_tier=RiskTier.BLOCKED,
                risk_factors=risk_factors,
                velocity_1h=0,
                velocity_24h=0,
                amount_deviation=0.0
            )

        # 2. Velocity Checks (DB or mock context)
        velocity_1h = 0
        velocity_24h = 0
        rapid_switching = False

        if db and customer_id:
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            one_day_ago = datetime.utcnow() - timedelta(hours=24)
            
            recent_txns = db.query(Transaction).filter(
                Transaction.customer_id == customer_id,
                Transaction.created_at >= one_day_ago
            ).all()

            velocity_24h = len(recent_txns)
            velocity_1h = sum(1 for t in recent_txns if t.created_at and t.created_at >= one_hour_ago)
            
            # Check unique payment methods/cards attempted in past 24h
            unique_methods = set(t.payment_method for t in recent_txns if t.payment_method)
            if len(unique_methods) >= 3:
                rapid_switching = True
        else:
            # Fallback estimation from transaction payload if db session not available
            velocity_1h = int(transaction.get("velocity_1h", 1))
            velocity_24h = int(transaction.get("velocity_24h", 2))
            rapid_switching = transaction.get("rapid_instrument_switching", False)

        # Velocity risk scoring
        if velocity_1h >= 5:
            risk_score += 45.0
            risk_factors.append(f"High 1-hour failure velocity ({velocity_1h} attempts in 60 mins)")
        elif velocity_1h >= 3:
            risk_score += 20.0
            risk_factors.append(f"Moderate 1-hour velocity ({velocity_1h} attempts)")

        if velocity_24h >= 10:
            risk_score += 30.0
            risk_factors.append(f"Excessive 24-hour failure count ({velocity_24h} failures)")

        if rapid_switching:
            risk_score += 25.0
            risk_factors.append("Rapid switching between multiple payment instruments detected")

        # 3. Amount Deviation Analysis
        historical_avg = 5000.0
        if customer:
            ltv = float(customer.get("lifetime_value", 50000.0))
            txn_count = max(int(customer.get("total_transactions", 5)), 1)
            historical_avg = max(ltv / txn_count, 1000.0)

        deviation_ratio = amount / historical_avg if historical_avg > 0 else 1.0

        if deviation_ratio >= 4.0 and amount >= 25000.0:
            risk_score += 25.0
            risk_factors.append(f"Significant transaction amount deviation ({deviation_ratio:.1f}x historical average)")
        elif deviation_ratio >= 2.5:
            risk_score += 10.0
            risk_factors.append(f"Moderate amount elevation ({deviation_ratio:.1f}x historical average)")

        # 4. Retry Fatigue Check
        retry_count = int(transaction.get("retry_count", 0))
        if retry_count >= 4:
            risk_score += 20.0
            risk_factors.append(f"Excessive previous retries ({retry_count} prior attempts)")

        # Clamp risk score
        risk_score = round(min(100.0, max(0.0, risk_score)), 1)

        # Determine Risk Tier
        if risk_score >= 80.0:
            tier = RiskTier.BLOCKED
        elif risk_score >= 50.0:
            tier = RiskTier.HIGH_RISK
        elif risk_score >= 25.0:
            tier = RiskTier.MEDIUM_RISK
        else:
            tier = RiskTier.LOW_RISK

        if not risk_factors:
            risk_factors.append("Standard velocity and typical spending profile")

        return cls._build_result(
            risk_score=risk_score,
            risk_tier=tier,
            risk_factors=risk_factors,
            velocity_1h=velocity_1h,
            velocity_24h=velocity_24h,
            amount_deviation=round(deviation_ratio, 2)
        )

    @classmethod
    def _build_result(
        cls,
        risk_score: float,
        risk_tier: str,
        risk_factors: List[str],
        velocity_1h: int,
        velocity_24h: int,
        amount_deviation: float
    ) -> Dict[str, Any]:
        allow_autonomous = (risk_tier == RiskTier.LOW_RISK)
        requires_fraud_review = (risk_tier in [RiskTier.HIGH_RISK, RiskTier.BLOCKED])

        return {
            "risk_score": risk_score,
            "risk_tier": risk_tier,
            "risk_factors": risk_factors,
            "allow_autonomous_recovery": allow_autonomous,
            "requires_fraud_review": requires_fraud_review,
            "metrics": {
                "velocity_1h": velocity_1h,
                "velocity_24h": velocity_24h,
                "amount_deviation_ratio": amount_deviation
            }
        }


risk_engine = RiskEngine()

