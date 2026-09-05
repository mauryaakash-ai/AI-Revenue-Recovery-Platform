"""
Real-Time Payment Webhook Engine & Provider Abstraction Layer
Supports:
1. Razorpay Webhooks (HMAC-SHA256 signature verification)
2. Stripe Webhooks (HMAC-SHA256 signature verification)
3. Generic Payment Gateway Webhooks (Token/Signature verification)

Pipeline:
Gateway Event -> Signature Check -> Idempotency Guard -> Normalization -> Transaction Record -> RevPilot Recovery Trigger
"""

import os
import hmac
import hashlib
import json
import logging
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from app.models import WebhookEvent, Transaction, Customer, Merchant, RecoveryOpportunity, TransactionStatus

logger = logging.getLogger("revpilot.webhooks")


class WebhookVerificationError(Exception):
    """Raised when signature verification fails"""
    pass


class WebhookDuplicateError(Exception):
    """Raised when an event has already been processed"""
    pass


class BaseWebhookHandler:
    def __init__(self, provider: str, secret_env_var: str):
        self.provider = provider
        self.secret = os.getenv(secret_env_var, f"mock_secret_{provider}")

    def verify_signature(self, raw_body: bytes, signature: Optional[str]) -> bool:
        """Base signature verification using HMAC-SHA256"""
        if not signature:
            # In test/demo environment, allow test signatures
            return os.getenv("ENVIRONMENT", "development") == "development"
        try:
            expected = hmac.new(
                self.secret.encode("utf-8"),
                raw_body,
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(expected, signature)
        except Exception as e:
            logger.warning(f"Signature check exception for {self.provider}: {e}")
            return False

    def generate_idempotency_key(self, raw_body: bytes, event_id: Optional[str] = None) -> str:
        """Generate a deterministic deduplication hash"""
        if event_id:
            return f"{self.provider}_{event_id}"
        return f"{self.provider}_{hashlib.sha256(raw_body).hexdigest()}"

    def normalize_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize to internal RevPilot event structure"""
        raise NotImplementedError


class RazorpayWebhookHandler(BaseWebhookHandler):
    def __init__(self):
        super().__init__("razorpay", "RAZORPAY_WEBHOOK_SECRET")

    def normalize_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        event_type = payload.get("event", "payment.failed")
        payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})

        amount_paise = payment_entity.get("amount", 0)
        amount_inr = float(amount_paise) / 100.0 if amount_paise > 0 else float(payload.get("amount", 14500.0))

        raw_method = payment_entity.get("method", "card")
        method = "card" if "card" in raw_method else ("upi" if "upi" in raw_method else ("netbanking" if "netbanking" in raw_method else "wallet"))

        error_code = payment_entity.get("error_code", "BAD_REQUEST_PAYMENT_DECLINED")
        error_desc = payment_entity.get("error_description", "Payment was declined by issuer bank / timeout")

        return {
            "provider": "razorpay",
            "event_type": event_type,
            "provider_payment_id": payment_entity.get("id", f"pay_{uuid.uuid4().hex[:14]}"),
            "provider_order_id": payment_entity.get("order_id", f"order_{uuid.uuid4().hex[:14]}"),
            "amount": amount_inr,
            "currency": payment_entity.get("currency", "INR"),
            "payment_method": method,
            "bank_name": payment_entity.get("bank") or "HDFC Bank",
            "customer_email": payment_entity.get("email", "customer@example.com"),
            "customer_phone": payment_entity.get("contact", "+91 98201 94821"),
            "failure_code": error_code,
            "failure_reason": error_desc,
            "failure_type": "temporary" if "timeout" in error_desc.lower() or "3ds" in error_desc.lower() else "permanent",
            "raw_payload": payload
        }


class StripeWebhookHandler(BaseWebhookHandler):
    def __init__(self):
        super().__init__("stripe", "STRIPE_WEBHOOK_SECRET")

    def normalize_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        event_type = payload.get("type", "payment_intent.payment_failed")
        data_obj = payload.get("data", {}).get("object", {})

        amount_cents = data_obj.get("amount", 0)
        amount = float(amount_cents) / 100.0 if amount_cents > 0 else float(payload.get("amount", 85.0))
        currency = data_obj.get("currency", "usd").upper()

        last_error = data_obj.get("last_payment_error", {})
        decline_code = last_error.get("decline_code") or last_error.get("code") or "card_declined"
        message = last_error.get("message", "The card was declined or 3DS authentication timed out.")

        charges = data_obj.get("charges", {}).get("data", [])
        payment_method = "card"
        if charges and len(charges) > 0:
            payment_method_details = charges[0].get("payment_method_details", {})
            payment_method = payment_method_details.get("type", "card")

        return {
            "provider": "stripe",
            "event_type": event_type,
            "provider_payment_id": data_obj.get("id", f"pi_{uuid.uuid4().hex[:14]}"),
            "provider_order_id": data_obj.get("id", f"pi_{uuid.uuid4().hex[:14]}"),
            "amount": amount,
            "currency": currency,
            "payment_method": payment_method,
            "bank_name": "International Acquirer",
            "customer_email": data_obj.get("receipt_email", "stripe_customer@example.com"),
            "customer_phone": "+1 415 555 2671",
            "failure_code": decline_code,
            "failure_reason": message,
            "failure_type": "temporary" if decline_code in ("try_again_later", "processing_error") else "permanent",
            "raw_payload": payload
        }


class GenericWebhookHandler(BaseWebhookHandler):
    def __init__(self):
        super().__init__("generic", "GENERIC_WEBHOOK_SECRET")

    def normalize_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "provider": payload.get("provider", "generic"),
            "event_type": payload.get("event_type", "payment.failed"),
            "provider_payment_id": payload.get("payment_id", f"gen_pay_{uuid.uuid4().hex[:10]}"),
            "provider_order_id": payload.get("order_id", f"gen_ord_{uuid.uuid4().hex[:10]}"),
            "amount": float(payload.get("amount", 5000.0)),
            "currency": payload.get("currency", "INR"),
            "payment_method": payload.get("payment_method", "upi"),
            "bank_name": payload.get("bank_name", "State Bank of India"),
            "customer_email": payload.get("customer_email", "generic_user@example.com"),
            "customer_phone": payload.get("customer_phone", "+91 98765 43210"),
            "failure_code": payload.get("failure_code", "GENERIC_FAILURE"),
            "failure_reason": payload.get("failure_reason", "Payment verification timeout"),
            "failure_type": payload.get("failure_type", "temporary"),
            "raw_payload": payload
        }


class WebhookEngine:
    """Orchestrates signature verification, deduplication, transaction creation, and recovery trigger"""

    def __init__(self):
        self.handlers = {
            "razorpay": RazorpayWebhookHandler(),
            "stripe": StripeWebhookHandler(),
            "generic": GenericWebhookHandler()
        }
        self._seen_keys = set()

    def process_webhook(
        self,
        provider: str,
        raw_body: bytes,
        signature: Optional[str],
        merchant_id: str = "merchant_urbankart",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        handler = self.handlers.get(provider.lower(), self.handlers["generic"])

        # 1. Signature Verification
        is_valid = handler.verify_signature(raw_body, signature)
        if not is_valid and os.getenv("ENVIRONMENT") != "development":
            raise WebhookVerificationError(f"Invalid webhook signature for {provider}")

        # Parse JSON
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except Exception as e:
            raise ValueError(f"Malformed JSON payload: {e}")

        event_id = payload.get("id") or payload.get("event_id")
        idempotency_key = handler.generate_idempotency_key(raw_body, event_id)

        # 2. Idempotency Check: Prevent duplicate event processing
        if db is not None:
            existing = db.query(WebhookEvent).filter(WebhookEvent.idempotency_key == idempotency_key).first()
            if existing:
                return {
                    "status": "duplicate",
                    "message": "Duplicate event detected. Event has already been processed safely.",
                    "event_id": existing.id,
                    "idempotency_key": idempotency_key,
                    "normalized_transaction_id": existing.normalized_transaction_id
                }
        else:
            if idempotency_key in self._seen_keys:
                return {
                    "status": "duplicate",
                    "message": "Duplicate event detected. Duplicate webhook event ignored safely.",
                    "event_id": f"whk_dedup_{idempotency_key[:10]}",
                    "idempotency_key": idempotency_key,
                    "normalized_transaction_id": f"TXN_{idempotency_key[:8]}"
                }
            self._seen_keys.add(idempotency_key)

        normalized = handler.normalize_event(payload)
        txn_id = normalized.get("provider_payment_id") or f"TXN_{uuid.uuid4().hex[:10].upper()}"

        if db is None:
            return {
                "status": "received",
                "message": f"Successfully validated and normalized {provider} webhook event.",
                "webhook_id": f"whk_{uuid.uuid4().hex[:14]}",
                "idempotency_key": idempotency_key,
                "transaction_id": txn_id,
                "normalized": normalized
            }

        # 3. Store raw webhook record
        webhook_event = WebhookEvent(
            id=f"whk_{uuid.uuid4().hex[:14]}",
            merchant_id=merchant_id,
            provider=provider,
            event_type=payload.get("event") or payload.get("type") or "payment.failed",
            event_id=event_id,
            idempotency_key=idempotency_key,
            signature=signature,
            payload=json.dumps(payload),
            status="received",
            received_at=datetime.utcnow()
        )
        db.add(webhook_event)
        db.commit()

        # 4. Normalize event
        normalized = handler.normalize_event(payload)

        # 5. Find or create Customer
        customer = db.query(Customer).filter(
            Customer.merchant_id == merchant_id,
            Customer.email == normalized["customer_email"]
        ).first()

        if not customer:
            customer = Customer(
                id=f"CUST_{uuid.uuid4().hex[:8]}",
                merchant_id=merchant_id,
                name=normalized["customer_email"].split("@")[0].capitalize(),
                email=normalized["customer_email"],
                phone=normalized["customer_phone"],
                segment="standard",
                lifetime_value=normalized["amount"] * 4.5,
                preferred_payment_method=normalized["payment_method"],
                typical_hour_start=19,
                typical_hour_end=22,
                historical_recovery_rate=0.82
            )
            db.add(customer)
            db.commit()

        # 6. Create Transaction Record
        txn_id = f"TXN_{uuid.uuid4().hex[:10].upper()}"
        transaction = Transaction(
            id=txn_id,
            merchant_id=merchant_id,
            customer_id=customer.id,
            amount=normalized["amount"],
            currency=normalized["currency"],
            payment_method=normalized["payment_method"],
            bank_name=normalized["bank_name"],
            status=TransactionStatus.FAILED,
            failure_reason=normalized["failure_reason"],
            failure_code=normalized["failure_code"],
            failure_type=normalized["failure_type"],
            risk_score=14.0,
            order_id=normalized["provider_order_id"],
            created_at=datetime.utcnow()
        )
        db.add(transaction)

        # 7. Create Recovery Opportunity
        prob = 0.88 if normalized["payment_method"] == "upi" else 0.74
        expected_recov = round(normalized["amount"] * prob, 2)
        opp = RecoveryOpportunity(
            id=f"OPP_{uuid.uuid4().hex[:10]}",
            transaction_id=txn_id,
            merchant_id=merchant_id,
            customer_id=customer.id,
            amount=normalized["amount"],
            recovery_probability=prob,
            expected_recovery=expected_recov,
            recommended_action="DISPATCH_WHATSAPP_UPI_INTENT" if normalized["payment_method"] in ("upi", "card") else "DELAYED_CARD_RETRY",
            priority="high" if normalized["amount"] >= 10000 else "medium",
            status="identified",
            explainability_reasons=json.dumps([
                f"Ingested from live {provider.upper()} webhook ({normalized['failure_code']})",
                f"Customer {customer.name} exhibits {customer.historical_recovery_rate*100:.0f}% historical recovery affinity",
                f"Expected Net Recovered Value: Rs.{expected_recov:,.2f}"
            ]),
            created_at=datetime.utcnow()
        )
        db.add(opp)

        # Update webhook event as processed
        webhook_event.status = "processed"
        webhook_event.normalized_transaction_id = txn_id
        webhook_event.processed_at = datetime.utcnow()
        db.commit()

        return {
            "status": "processed",
            "message": f"Successfully ingested {provider} webhook and triggered RevPilot recovery pipeline.",
            "webhook_id": webhook_event.id,
            "idempotency_key": idempotency_key,
            "transaction_id": txn_id,
            "opportunity_id": opp.id,
            "normalized": normalized
        }


webhook_engine = WebhookEngine()
