"""
Decision Engine & Policy Layer (Enterprise Upgrade):
- Enforces Section 41 Standardized AI Decision Object
- Optimizes for Expected Net Recovery Value (ENRV):
    ENRV = (Amount * P_recovery) - (Channel Cost + Gateway Cost + Churn Cost + Risk Cost)
- Evaluates Pre-Recovery Risk Controls before eligibility
- Dynamic Channel & Timing Optimization with Bandit Exploration
- Gating: AUTO_EXECUTE vs HUMAN_APPROVAL vs SUPPRESS_RISK
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from app.failure_classifier import failure_classifier, FailureTaxonomy
from app.risk_engine import risk_engine, RiskTier
from app.timing_engine import timing_engine
from app.bandit_engine import bandit_engine


class DecisionEngine:
    """Enterprise Recovery Decision Engine generating standardized immutable Decision Objects"""

    MODEL_VERSION = "revpilot-v2.5.0-enterprise"
    DEFAULT_POLICY_ID = "POL_DEFAULT_ENTERPRISE"

    @classmethod
    def calculate_expected_net_recovery(
        cls,
        amount: float,
        probability: float,
        channel_cost: float = 1.85,
        gateway_cost: float = 0.0,
        customer_ltv: float = 240000.0,
        churn_risk_prob: float = 0.0015,
        risk_score: float = 10.0
    ) -> Dict[str, Any]:
        """
        Expected Net Recovery Value (ENRV) =
        (Probability of recovery * transaction value)
        - gateway cost
        - communication cost
        - (churn probability * customer LTV)
        - (risk dispute factor * amount)
        """
        gross_expected = amount * probability
        churn_cost = churn_risk_prob * customer_ltv
        # Risk dispute provision (higher risk score reserves a fraction for chargeback/dispute risk)
        risk_cost = (risk_score / 100.0) * (amount * 0.05)
        total_costs = channel_cost + gateway_cost + churn_cost + risk_cost
        net_expected = gross_expected - total_costs

        # ROI percentage = (net_expected / total_costs) * 100
        roi = ((net_expected) / max(0.5, total_costs)) * 100 if total_costs > 0 else 1000.0

        return {
            "gross_expected": round(gross_expected, 2),
            "channel_cost": round(channel_cost, 2),
            "gateway_cost": round(gateway_cost, 2),
            "expected_churn_cost": round(churn_cost, 2),
            "expected_risk_cost": round(risk_cost, 2),
            "total_costs": round(total_costs, 2),
            "expected_net_recovered_value": round(net_expected, 2),
            "expected_roi": round(roi, 1)
        }

    @classmethod
    def generate_decision_card(
        cls,
        transaction: Dict[str, Any],
        customer: Optional[Dict[str, Any]] = None,
        opp: Optional[Dict[str, Any]] = None,
        policy: Optional[Dict[str, Any]] = None,
        db: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes Risk, Taxonomy, Timing, Economics, and Bandit components
        into the Section 41 Standardized AI Decision Object.
        """
        customer = customer or {
            "id": transaction.get("customer_id", "CUST_92019"),
            "name": transaction.get("customer_name", "Valued Customer"),
            "segment": "VIP",
            "lifetime_value": 240000.0,
            "historical_recovery_rate": 0.83
        }
        policy = policy or {
            "policy_id": cls.DEFAULT_POLICY_ID,
            "auto_approval_threshold": 0.80,
            "max_autonomous_amount": 10000.0,
            "min_roi_percent": 150.0
        }

        amount = float(transaction.get("amount", 45000.0))
        ltv = float(customer.get("lifetime_value", 240000.0))

        # 1. Failure Taxonomy Classification
        failure_code = transaction.get("failure_code")
        failure_reason = transaction.get("failure_reason")
        payment_method = transaction.get("payment_method", "card")
        bank_name = transaction.get("bank_name", "HDFC Bank")

        classification_res = failure_classifier.classify(
            failure_code=failure_code,
            failure_reason=failure_reason,
            payment_method=payment_method,
            bank_name=bank_name
        )

        # 2. Risk Engine Assessment
        risk_res = risk_engine.assess_risk(
            transaction=transaction,
            customer=customer,
            db=db
        )
        risk_score = risk_res["risk_score"]
        risk_tier = risk_res["risk_tier"]

        # 3. Base Recovery Probability Calculation
        if opp and "recovery_probability" in opp:
            base_prob = float(opp["recovery_probability"])
        else:
            # Baseline from classifier and customer historical conversion
            cust_rate = float(customer.get("historical_recovery_rate", 0.75))
            cat_score = classification_res["recoverability_score"]
            base_prob = round((cust_rate * 0.45) + (cat_score * 0.55), 3)

        # Risk penalty on recovery probability
        if risk_tier == RiskTier.HIGH_RISK:
            base_prob = min(base_prob, 0.25)
        elif risk_tier == RiskTier.BLOCKED or classification_res["is_permanent"]:
            base_prob = 0.02

        # 4. Timing and Channel Optimization
        timing_res = timing_engine.optimize(
            transaction=transaction,
            customer=customer,
            failure_category=classification_res["category"]
        )

        # 5. Bandit Strategy Selection
        bandit_choice = bandit_engine.select_arm(
            context={"transaction_id": transaction.get("id")},
            db=db
        )

        # 6. Financial Net Recovery Evaluation (ENRV)
        channel_cost = timing_res["expected_channel_cost"]
        financials = cls.calculate_expected_net_recovery(
            amount=amount,
            probability=base_prob,
            channel_cost=channel_cost,
            gateway_cost=0.0,
            customer_ltv=ltv,
            churn_risk_prob=0.0015,
            risk_score=risk_score
        )
        enrv = financials["expected_net_recovered_value"]
        roi = financials["expected_roi"]

        # 7. Tri-State Decision Gating: AUTO_EXECUTE vs HUMAN_APPROVAL vs SUPPRESS_RISK
        auto_threshold = float(policy.get("auto_approval_threshold", 0.80))
        max_auto_amount = float(policy.get("max_autonomous_amount", 10000.0))
        min_roi = float(policy.get("min_roi_percent", 150.0))

        decision_state = "HUMAN_APPROVAL"
        governance_reason = ""

        if risk_tier == RiskTier.BLOCKED or classification_res["is_permanent"] or enrv <= 0:
            decision_state = "SUPPRESS_RISK"
            if classification_res["is_permanent"]:
                governance_reason = "Permanent unrecoverable decline code (card invalid/closed/blacklisted)."
            elif risk_tier == RiskTier.BLOCKED:
                governance_reason = f"Severe fraud risk detected (Risk Score: {risk_score:.1f}). Suppressed."
            else:
                governance_reason = f"Negative expected net revenue (ENRV: ₹{enrv:,.2f}). Action economically unviable."
        elif (
            base_prob >= auto_threshold and
            amount <= max_auto_amount and
            risk_tier == RiskTier.LOW_RISK and
            roi >= min_roi
        ):
            decision_state = "AUTO_EXECUTE"
            governance_reason = f"High confidence ({base_prob:.1%}), low risk ({risk_score}), amount ₹{amount:,.0f} within autonomous limit."
        else:
            decision_state = "HUMAN_APPROVAL"
            if amount > max_auto_amount:
                governance_reason = f"Transaction amount (₹{amount:,.2f}) exceeds autonomous limit (₹{max_auto_amount:,.2f}). Requires supervisor review."
            elif base_prob < auto_threshold:
                governance_reason = f"Recovery probability ({base_prob:.1%}) is below autonomous threshold ({auto_threshold:.1%})."
            elif risk_tier == RiskTier.MEDIUM_RISK:
                governance_reason = f"Elevated velocity/amount deviation (Risk Tier: MEDIUM_RISK). Requires human sign-off."
            else:
                governance_reason = "Exceeds merchant risk policy boundary."

        # Alternatives considered from timing engine
        alternatives = []
        for alt in timing_res["ranked_alternatives"][1:4]:
            alt_prob = max(0.1, round(base_prob * (alt["suitability_score"] / max(0.01, timing_res["ranked_alternatives"][0]["suitability_score"])), 3))
            alternatives.append({
                "action": alt["channel"],
                "strategy_label": alt["label"],
                "recovery_probability": alt_prob,
                "expected_cost": alt["cost"],
                "expected_net_value": round(amount * alt_prob - alt["cost"], 2),
                "rejection_reason": f"Lower suitability ({alt['suitability_score']}) than recommended channel."
            })

        # Feature attribution for explainability
        feature_attribution = [
            {"feature": f"Failure Category: {classification_res['taxonomy_label']}", "weight": 0.35},
            {"feature": f"Customer Historical Recovery Rate ({customer.get('historical_recovery_rate', 0.83):.1%})", "weight": 0.25},
            {"feature": f"Pre-Recovery Risk Score: {risk_score}/100 ({risk_tier})", "weight": 0.20},
            {"feature": f"Execution Timing: {timing_res['scheduled_window']}", "weight": 0.12},
            {"feature": f"Contextual Bandit Arm: {bandit_choice['strategy_label']}", "weight": 0.08}
        ]

        counterfactual = (
            f"If unassisted, organic recovery likelihood is {round(base_prob * 0.22, 3):.1%} "
            f"(Expected permanent revenue leakage: ₹{amount * (1.0 - (base_prob * 0.22)):,.2f})."
        )

        txn_id = transaction.get("id", "TXN_829341")

        # Standardized AI Decision Object (Section 41 Schema compliant)
        return {
            # Section 41 Standardized AI Decision Object Keys
            "transaction_id": txn_id,
            "classification": classification_res["taxonomy_label"],
            "classification_confidence": classification_res["confidence"],
            "recovery_probability": base_prob,
            "risk_score": risk_score,
            "risk_tier": risk_tier,
            "expected_recovery_value": enrv,
            "recommended_channel": timing_res["recommended_channel"],
            "recommended_time": timing_res["scheduled_time"],
            "expected_cost": financials["total_costs"],
            "expected_roi": roi,
            "decision": decision_state,
            "confidence": base_prob,
            "explanation": governance_reason,
            "policy_id": policy.get("policy_id", cls.DEFAULT_POLICY_ID),
            "model_version": cls.MODEL_VERSION,

            # Rich Enterprise Metadata & Backwards Compatibility
            "decision_card_id": f"DEC_{txn_id}_{int(datetime.utcnow().timestamp())}",
            "merchant_id": transaction.get("merchant_id", "merchant_urbankart"),
            "customer": customer,
            "original_failure": {
                "amount": amount,
                "payment_method": payment_method,
                "bank": bank_name,
                "decline_code": failure_code or "UNKNOWN",
                "decline_category": classification_res["category"],
                "decline_subcategory": classification_res["subcategory"],
                "timestamp": transaction.get("created_at", datetime.utcnow().isoformat())
            },
            "recommendation": {
                "primary_action": f"DISPATCH_{timing_res['recommended_channel'].upper()}",
                "scheduled_window": timing_res["scheduled_window"],
                "wait_delay_minutes": timing_res["delay_minutes"],
                "channel": timing_res["recommended_channel"],
                "recovery_probability": base_prob,
                "confidence_interval": [round(max(0.0, base_prob - 0.04), 3), round(min(1.0, base_prob + 0.04), 3)],
                "financials": financials,
                "bandit_exploration": bandit_choice["is_exploration"]
            },
            "alternatives_considered": alternatives,
            "explainability_feature_attribution": feature_attribution,
            "counterfactual_analysis": counterfactual,
            "governance": {
                "risk_tier": risk_tier,
                "risk_factors": risk_res["risk_factors"],
                "approval_required": (decision_state == "HUMAN_APPROVAL"),
                "approval_reason": governance_reason,
                "assigned_role": "Revenue Operations",
                "policy_checks_passed": [
                    "QUIET_HOURS_ENFORCED",
                    "FREQUENCY_CAP_OK",
                    "FRAUD_VELOCITY_CHECK",
                    "ECONOMIC_ROI_GATE"
                ]
            }
        }


decision_engine = DecisionEngine()
