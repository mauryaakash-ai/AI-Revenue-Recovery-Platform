"""
Hierarchical Failure Classification Engine
Taxonomy:
- Issuer: timeout, decline, bank_unavailable
- Gateway: timeout, api_failure, routing_failure
- Authentication: 3ds_timeout, otp_failure, authentication_rejection
- Customer: insufficient_funds, limit_exceeded, expired_instrument
- Permanent: invalid_instrument, permanent_rejection, blacklisted
"""

from typing import Dict, Any, Tuple, Optional
import re
from datetime import datetime


class FailureTaxonomy:
    # Top-level Categories
    ISSUER = "ISSUER"
    GATEWAY = "GATEWAY"
    AUTHENTICATION = "AUTHENTICATION"
    CUSTOMER = "CUSTOMER"
    PERMANENT = "PERMANENT"

    TAXONOMY_MAP = {
        ISSUER: {
            "timeout": "Issuer Bank Timed Out",
            "decline": "Issuer Bank Declined Transaction",
            "bank_unavailable": "Issuer Core Banking System Unavailable / Maintenance"
        },
        GATEWAY: {
            "timeout": "Acquiring Gateway Latency Timeout",
            "api_failure": "Gateway Communication / API Error",
            "routing_failure": "Smart Routing Switch Failure"
        },
        AUTHENTICATION: {
            "3ds_timeout": "3D-Secure ACS Timeout During Verification",
            "otp_failure": "OTP Expired or Incorrect Input",
            "authentication_rejection": "Customer Aborted Authentication Challenge"
        },
        CUSTOMER: {
            "insufficient_funds": "Customer Account Has Insufficient Balance",
            "limit_exceeded": "Customer Daily/Per-Transaction Card Limit Exceeded",
            "expired_instrument": "Card Expired or Mandate Elapsed"
        },
        PERMANENT: {
            "invalid_instrument": "Invalid Card/Account/VPA Information",
            "permanent_rejection": "Account Closed, Frozen or Restricted by Bank",
            "blacklisted": "Instrument Blacklisted for Fraud or Risk"
        }
    }


class FailureClassifier:
    """Classifies transaction failures into hierarchical taxonomy with confidence attribution"""

    KEYWORD_RULES = [
        # Permanent
        (r"(invalid|incorrect|does not exist|no such) (card|vpa|account|cvv|expiry)", FailureTaxonomy.PERMANENT, "invalid_instrument", 0.96),
        (r"(account (closed|frozen|blocked|restricted)|stolen card|lost card)", FailureTaxonomy.PERMANENT, "permanent_rejection", 0.98),
        (r"(blacklisted|fraud block|sanctioned)", FailureTaxonomy.PERMANENT, "blacklisted", 0.99),

        # Authentication
        (r"(3ds|acs|3d-secure|challenge).*?(timeout|timed out|expired)", FailureTaxonomy.AUTHENTICATION, "3ds_timeout", 0.94),
        (r"(otp|pin).*?(incorrect|wrong|expired|max attempts)", FailureTaxonomy.AUTHENTICATION, "otp_failure", 0.92),
        (r"(user cancelled|aborted|authentication failed|auth rejected)", FailureTaxonomy.AUTHENTICATION, "authentication_rejection", 0.90),

        # Customer
        (r"(insufficient (fund|balance)|low balance|no balance)", FailureTaxonomy.CUSTOMER, "insufficient_funds", 0.95),
        (r"(limit (exceeded|reached)|velocity limit|daily limit)", FailureTaxonomy.CUSTOMER, "limit_exceeded", 0.91),
        (r"(card expired|expired instrument|mandate expired)", FailureTaxonomy.CUSTOMER, "expired_instrument", 0.93),

        # Gateway
        (r"(gateway (timeout|down|error)|switch failure|routing (failed|error))", FailureTaxonomy.GATEWAY, "routing_failure", 0.91),
        (r"(api (error|failure|exception)|connection reset|gateway error 5\d\d)", FailureTaxonomy.GATEWAY, "api_failure", 0.89),

        # Issuer
        (r"(bank (timeout|timed out|not responding)|issuer timeout)", FailureTaxonomy.ISSUER, "timeout", 0.92),
        (r"(issuer (down|unavailable|maintenance)|core banking down)", FailureTaxonomy.ISSUER, "bank_unavailable", 0.94),
        (r"(bank decline|do not honor|issuer declined)", FailureTaxonomy.ISSUER, "decline", 0.86),
    ]

    CODE_MAP = {
        # Razorpay Codes
        "BAD_REQUEST_PAYMENT_TIMED_OUT": (FailureTaxonomy.ISSUER, "timeout", 0.91),
        "BAD_REQUEST_PAYMENT_DECLINED_BY_BANK": (FailureTaxonomy.ISSUER, "decline", 0.88),
        "GATEWAY_ERROR": (FailureTaxonomy.GATEWAY, "api_failure", 0.90),
        "GATEWAY_TIMEOUT": (FailureTaxonomy.GATEWAY, "timeout", 0.92),
        "BAD_REQUEST_PAYMENT_OTP_INCORRECT": (FailureTaxonomy.AUTHENTICATION, "otp_failure", 0.95),
        "BAD_REQUEST_PAYMENT_VERIFICATION_FAILED": (FailureTaxonomy.AUTHENTICATION, "3ds_timeout", 0.89),
        "BAD_REQUEST_PAYMENT_ACCOUNT_INSUFFICIENT_BALANCE": (FailureTaxonomy.CUSTOMER, "insufficient_funds", 0.97),
        "BAD_REQUEST_PAYMENT_CARD_LIMIT_EXCEEDED": (FailureTaxonomy.CUSTOMER, "limit_exceeded", 0.93),
        "BAD_REQUEST_PAYMENT_CARD_EXPIRED": (FailureTaxonomy.CUSTOMER, "expired_instrument", 0.96),
        "BAD_REQUEST_PAYMENT_CARD_INVALID": (FailureTaxonomy.PERMANENT, "invalid_instrument", 0.98),
        
        # Stripe Codes
        "card_declined": (FailureTaxonomy.ISSUER, "decline", 0.85),
        "insufficient_funds": (FailureTaxonomy.CUSTOMER, "insufficient_funds", 0.96),
        "expired_card": (FailureTaxonomy.CUSTOMER, "expired_instrument", 0.97),
        "incorrect_cvc": (FailureTaxonomy.PERMANENT, "invalid_instrument", 0.94),
        "processing_error": (FailureTaxonomy.GATEWAY, "api_failure", 0.88),
        "authentication_required": (FailureTaxonomy.AUTHENTICATION, "authentication_rejection", 0.90),
        "lost_card": (FailureTaxonomy.PERMANENT, "permanent_rejection", 0.99),
        "stolen_card": (FailureTaxonomy.PERMANENT, "permanent_rejection", 0.99)
    }

    @classmethod
    def classify(
        cls,
        failure_code: Optional[str] = None,
        failure_reason: Optional[str] = None,
        payment_method: Optional[str] = None,
        bank_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Classify failure with category, subcategory, confidence score, and recoverability indicator"""
        # 1. Exact code match
        if failure_code and failure_code in cls.CODE_MAP:
            category, subcategory, base_conf = cls.CODE_MAP[failure_code]
            return cls._build_result(category, subcategory, base_conf, f"Exact match for gateway code: {failure_code}")

        # 2. Textual regex pattern matching on failure reason
        search_text = f"{failure_code or ''} {failure_reason or ''}".lower()
        for pattern, cat, subcat, conf in cls.KEYWORD_RULES:
            if re.search(pattern, search_text):
                return cls._build_result(cat, subcat, conf, f"Rule match '{pattern}' in description")

        # 3. Fallback inference based on bank and payment method
        if "upi" in (payment_method or "").lower():
            return cls._build_result(
                FailureTaxonomy.ISSUER, 
                "timeout", 
                0.68, 
                "UPI transaction default to transient NPCI/PSP timeout"
            )

        return cls._build_result(
            FailureTaxonomy.ISSUER,
            "decline",
            0.60,
            "Generic bank decline fallback"
        )

    @classmethod
    def _build_result(cls, category: str, subcategory: str, confidence: float, explanation: str) -> Dict[str, Any]:
        is_permanent = (category == FailureTaxonomy.PERMANENT)
        # Permanent failures are unrecoverable; customer insufficient funds / auth timeouts are highly recoverable
        recoverable_weights = {
            FailureTaxonomy.AUTHENTICATION: 0.88,
            FailureTaxonomy.CUSTOMER: 0.74,
            FailureTaxonomy.ISSUER: 0.62,
            FailureTaxonomy.GATEWAY: 0.82,
            FailureTaxonomy.PERMANENT: 0.05
        }
        recoverable_score = recoverable_weights.get(category, 0.50)

        label = FailureTaxonomy.TAXONOMY_MAP.get(category, {}).get(subcategory, f"{category} - {subcategory}")

        return {
            "category": category,
            "subcategory": subcategory,
            "taxonomy_label": label,
            "confidence": round(confidence, 3),
            "is_permanent": is_permanent,
            "recoverability_score": recoverable_score,
            "explanation": explanation
        }


failure_classifier = FailureClassifier()
