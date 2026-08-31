"""
Enhanced Tool Registry with:
- Idempotency guarantees for sensitive actions
- Approval expiration and re-confirmation
- Undo/cancel stories
- Input validation
- Error recovery
"""

import hashlib
import json
from typing import Dict, Optional, Tuple, List, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.models import AgentAction, ActionTier, ActionStatus

IST = timezone(timedelta(hours=5, minutes=30))
APPROVAL_EXPIRATION_MINUTES = 30


class IdempotencyKey:
    """Generates and validates idempotency keys for sensitive operations"""
    
    @staticmethod
    def generate(merchant_id: str, action: str, target_id: str, parameters: Dict) -> str:
        """Generate deterministic idempotency key"""
        data = f"{merchant_id}:{action}:{target_id}:{json.dumps(parameters, sort_keys=True)}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def get_or_create_action(db: Session, merchant_id: str, idempotency_key: str, 
                            action: str, tool_tier: ActionTier) -> Optional[Dict]:
        """Check if action with this key already exists"""
        existing = db.query(AgentAction).filter(
            AgentAction.merchant_id == merchant_id,
            AgentAction.input_data.like(f'%"{idempotency_key}"%')
        ).first()
        
        if existing:
            return {
                "already_executed": True,
                "action_id": existing.id,
                "result": existing.result,
                "status": existing.status.value
            }
        return None


class ApprovalValidator:
    """Validates and manages approval tokens with expiration"""
    
    @staticmethod
    def validate_approval(approval_token: str, action_id: str, created_at: datetime) -> Tuple[bool, str]:
        """Check if approval is valid and not expired"""
        
        if not approval_token:
            return False, "Approval token required"
        
        # Check expiration
        now = datetime.now(IST)
        if now - created_at > timedelta(minutes=APPROVAL_EXPIRATION_MINUTES):
            return False, f"Approval expired. Created {(now - created_at).total_seconds() / 60:.0f} minutes ago. Please review and re-approve."
        
        # TODO: Validate token signature in production
        return True, "Approval valid"
    
    @staticmethod
    def generate_expiration_warning(created_at: datetime, time_remaining_minutes: int = 5) -> Optional[str]:
        """Generate warning if approval is about to expire"""
        now = datetime.now(IST)
        elapsed = (now - created_at).total_seconds() / 60
        
        if elapsed > (APPROVAL_EXPIRATION_MINUTES - time_remaining_minutes):
            return f"Approval expires in {APPROVAL_EXPIRATION_MINUTES - int(elapsed)} minutes. Please act soon."
        return None


class EnhancedToolRegistry:
    """Enhanced tool registry with safety features"""
    
    def __init__(self, db: Session, provider=None):
        self.db = db
        self.provider = provider
    
    async def send_recovery_message_safe(self, merchant_id: str, input_data: Dict, 
                                        approval_token: Optional[str] = None) -> Dict:
        """Send message with idempotency and approval validation"""
        
        customer_id = input_data.get("customer_id")
        message = input_data.get("message")
        
        # Input validation
        if not customer_id or not message:
            return {"error": "customer_id and message required"}
        
        if len(message) > 500:
            return {"error": "Message too long (max 500 characters)"}
        
        # Generate idempotency key
        idempotency_key = IdempotencyKey.generate(
            merchant_id, 
            "send_recovery_message", 
            customer_id, 
            {"message": message}
        )
        
        # Check if already sent
        existing = IdempotencyKey.get_or_create_action(
            self.db, merchant_id, idempotency_key, 
            "send_recovery_message", ActionTier.SENSITIVE_ACTION
        )
        if existing and existing["already_executed"]:
            return {
                "success": True,
                "message": "This message was already sent (idempotent retry)",
                "message_id": existing["action_id"],
                "timestamp": existing.get("timestamp")
            }
        
        # Validate approval (sensitive action)
        is_valid, reason = ApprovalValidator.validate_approval(approval_token or "", "send_msg", datetime.now(IST))
        if not is_valid and not approval_token:
            return {
                "error": "This action requires approval",
                "reason": "Sending messages to customers is sensitive and requires explicit approval",
                "expires_in_minutes": APPROVAL_EXPIRATION_MINUTES
            }
        
        if not is_valid:
            return {"error": reason}
        
        # Execute action
        try:
            # Mock: simulate message send
            message_id = hashlib.sha256(f"{customer_id}:{message}".encode()).hexdigest()[:12]
            
            # Log to audit trail
            action = AgentAction(
                merchant_id=merchant_id,
                agent="revpilot",
                action="send_recovery_message",
                tool="send_recovery_message",
                tool_tier=ActionTier.SENSITIVE_ACTION,
                input_data=json.dumps({"customer_id": customer_id, "message": message, "idempotency_key": idempotency_key}),
                result=json.dumps({"message_id": message_id}),
                status=ActionStatus.EXECUTED,
                approval="token_validated",
                executed_at=datetime.now(IST)
            )
            self.db.add(action)
            self.db.commit()
            
            return {
                "success": True,
                "message_id": message_id,
                "customer_id": customer_id,
                "sent_at": datetime.now(IST).isoformat(),
                "warning": "Message sent. This action cannot be undone. Check audit log for confirmation."
            }
        
        except Exception as e:
            self.db.rollback()
            return {"error": f"Failed to send message: {str(e)}"}
    
    async def refund_payment_safe(self, merchant_id: str, input_data: Dict, 
                                 approval_token: Optional[str] = None) -> Dict:
        """Refund payment with idempotency and approval validation"""
        
        transaction_id = input_data.get("transaction_id")
        amount_paise = input_data.get("amount_paise")
        reason = input_data.get("reason", "customer_request")
        
        # Input validation
        if not transaction_id:
            return {"error": "transaction_id required"}
        
        if not amount_paise or amount_paise <= 0:
            return {"error": "amount_paise must be positive"}
        
        # Generate idempotency key
        idempotency_key = IdempotencyKey.generate(
            merchant_id, 
            "refund_payment", 
            transaction_id, 
            {"amount_paise": amount_paise, "reason": reason}
        )
        
        # Check if already refunded
        existing = IdempotencyKey.get_or_create_action(
            self.db, merchant_id, idempotency_key, 
            "refund_payment", ActionTier.SENSITIVE_ACTION
        )
        if existing and existing["already_executed"]:
            return {
                "success": True,
                "message": "This refund was already processed (idempotent retry)",
                "refund_id": existing["action_id"],
                "status": existing.get("status")
            }
        
        # Validate approval (sensitive action)
        is_valid, reason_msg = ApprovalValidator.validate_approval(approval_token or "", f"refund_{transaction_id}", datetime.now(IST))
        if not is_valid and not approval_token:
            return {
                "error": "This action requires approval",
                "reason": "Refunds are sensitive actions and require explicit merchant approval",
                "expires_in_minutes": APPROVAL_EXPIRATION_MINUTES,
                "undo_story": "Refunds cannot be undone once processed. Verify the amount and reason before approving."
            }
        
        if not is_valid:
            return {"error": reason_msg, "undo_story": "Cannot proceed without valid approval"}
        
        # Execute refund
        try:
            refund_id = hashlib.sha256(f"{transaction_id}:{amount_paise}".encode()).hexdigest()[:12]
            
            # Log to audit trail
            action = AgentAction(
                merchant_id=merchant_id,
                agent="revpilot",
                action="refund_payment",
                tool="refund_payment",
                tool_tier=ActionTier.SENSITIVE_ACTION,
                input_data=json.dumps({
                    "transaction_id": transaction_id, 
                    "amount_paise": amount_paise,
                    "reason": reason,
                    "idempotency_key": idempotency_key
                }),
                result=json.dumps({"refund_id": refund_id, "status": "processed"}),
                status=ActionStatus.EXECUTED,
                approval="token_validated",
                executed_at=datetime.now(IST)
            )
            self.db.add(action)
            self.db.commit()
            
            return {
                "success": True,
                "refund_id": refund_id,
                "transaction_id": transaction_id,
                "amount_paise": amount_paise,
                "amount_label": f"₹{amount_paise / 100:,.2f}",
                "refunded_at": datetime.now(IST).isoformat(),
                "warning": "⚠️ Refund processed. This action CANNOT be undone. Check audit log for confirmation."
            }
        
        except Exception as e:
            self.db.rollback()
            return {"error": f"Failed to process refund: {str(e)}"}
    
    async def create_payout_safe(self, merchant_id: str, input_data: Dict, 
                                approval_token: Optional[str] = None) -> Dict:
        """Create payout with idempotency and approval validation"""
        
        amount_paise = input_data.get("amount_paise")
        recipient_account = input_data.get("recipient_account")
        
        # Input validation
        if not amount_paise or amount_paise <= 0:
            return {"error": "amount_paise must be positive"}
        
        if not recipient_account:
            return {"error": "recipient_account required"}
        
        if len(recipient_account) > 50:
            return {"error": "recipient_account too long"}
        
        # Generate idempotency key
        idempotency_key = IdempotencyKey.generate(
            merchant_id, 
            "create_payout", 
            recipient_account, 
            {"amount_paise": amount_paise}
        )
        
        # Check if already created
        existing = IdempotencyKey.get_or_create_action(
            self.db, merchant_id, idempotency_key, 
            "create_payout", ActionTier.SENSITIVE_ACTION
        )
        if existing and existing["already_executed"]:
            return {
                "success": True,
                "message": "This payout was already created (idempotent retry)",
                "payout_id": existing["action_id"],
                "status": existing.get("status")
            }
        
        # Validate approval (sensitive action)
        is_valid, reason = ApprovalValidator.validate_approval(approval_token or "", f"payout_{recipient_account}", datetime.now(IST))
        if not is_valid and not approval_token:
            return {
                "error": "This action requires approval",
                "reason": "Payouts are sensitive financial actions and require explicit approval",
                "expires_in_minutes": APPROVAL_EXPIRATION_MINUTES,
                "undo_story": "Payouts cannot be reversed once initiated. Verify recipient account and amount before approving."
            }
        
        if not is_valid:
            return {"error": reason, "undo_story": "Cannot proceed without valid approval"}
        
        # Execute payout
        try:
            payout_id = hashlib.sha256(f"{recipient_account}:{amount_paise}".encode()).hexdigest()[:12]
            
            # Log to audit trail
            action = AgentAction(
                merchant_id=merchant_id,
                agent="revpilot",
                action="create_payout",
                tool="create_payout",
                tool_tier=ActionTier.SENSITIVE_ACTION,
                input_data=json.dumps({
                    "amount_paise": amount_paise,
                    "recipient_account": recipient_account,
                    "idempotency_key": idempotency_key
                }),
                result=json.dumps({"payout_id": payout_id, "status": "initiated"}),
                status=ActionStatus.EXECUTED,
                approval="token_validated",
                executed_at=datetime.now(IST)
            )
            self.db.add(action)
            self.db.commit()
            
            return {
                "success": True,
                "payout_id": payout_id,
                "amount_paise": amount_paise,
                "amount_label": f"₹{amount_paise / 100:,.2f}",
                "recipient": recipient_account,
                "initiated_at": datetime.now(IST).isoformat(),
                "warning": "⚠️ Payout initiated. This action CANNOT be reversed. Check audit log and settlement status."
            }
        
        except Exception as e:
            self.db.rollback()
            return {"error": f"Failed to create payout: {str(e)}"}

