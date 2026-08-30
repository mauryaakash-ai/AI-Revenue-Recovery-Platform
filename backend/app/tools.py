"""
Action tools for RevPilot agent.
All tools are deterministic and log-safe.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import AgentAction, AuditLog, ActionTier, ActionStatus, Transaction, Customer
from app.providers import ProviderFactory, PaymentProvider
import uuid
import json


class ToolRegistry:
    """Registry of all available tools for the agent"""
    
    def __init__(self, db: Session, provider: Optional[PaymentProvider] = None):
        self.db = db
        self.provider = provider or ProviderFactory.get_default_provider()
        
        # Tool definitions with metadata
        self.tools = {
            # READ tier - no approval needed
            "get_revenue": {"tier": ActionTier.READ, "fn": self.get_revenue},
            "get_transactions": {"tier": ActionTier.READ, "fn": self.get_transactions},
            "get_failed_payments": {"tier": ActionTier.READ, "fn": self.get_failed_payments},
            "get_customers": {"tier": ActionTier.READ, "fn": self.get_customers},
            "get_customer_history": {"tier": ActionTier.READ, "fn": self.get_customer_history},
            "get_refunds": {"tier": ActionTier.READ, "fn": self.get_refunds},
            "detect_anomalies": {"tier": ActionTier.READ, "fn": self.detect_anomalies},
            "get_top_leaks": {"tier": ActionTier.READ, "fn": self.get_top_leaks},
            
            # ANALYZE tier - no approval needed
            "calculate_revenue_loss": {"tier": ActionTier.ANALYZE, "fn": self.calculate_revenue_loss},
            "calculate_revenue_at_risk": {"tier": ActionTier.ANALYZE, "fn": self.calculate_revenue_at_risk},
            "predict_recovery_probability": {"tier": ActionTier.ANALYZE, "fn": self.predict_recovery_probability},
            "segment_customers": {"tier": ActionTier.ANALYZE, "fn": self.segment_customers},
            "analyze_payment_methods": {"tier": ActionTier.ANALYZE, "fn": self.analyze_payment_methods},
            
            # RECOMMEND tier - no approval needed
            "recommend_recovery_campaign": {"tier": ActionTier.RECOMMEND, "fn": self.recommend_recovery_campaign},
            
            # LOW_RISK_ACTION tier - low approval barrier
            "create_payment_link": {"tier": ActionTier.LOW_RISK_ACTION, "fn": self.create_payment_link},
            "send_recovery_message": {"tier": ActionTier.LOW_RISK_ACTION, "fn": self.send_recovery_message},
            "get_campaign_results": {"tier": ActionTier.LOW_RISK_ACTION, "fn": self.get_campaign_results},
            
            # SENSITIVE_ACTION tier - requires explicit approval
            "refund_payment": {"tier": ActionTier.SENSITIVE_ACTION, "fn": self.refund_payment},
            "bulk_customer_campaign": {"tier": ActionTier.SENSITIVE_ACTION, "fn": self.bulk_customer_campaign},
            "create_payout": {"tier": ActionTier.SENSITIVE_ACTION, "fn": self.create_payout},
        }
    
    async def execute_tool(self, tool_name: str, merchant_id: str, input_data: Dict, 
                          approval_token: Optional[str] = None) -> Dict:
        """Execute a tool with approval gating"""
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}
        
        tool_def = self.tools[tool_name]
        tier = tool_def["tier"]
        fn = tool_def["fn"]
        
        # Check approval for sensitive actions
        if tier == ActionTier.SENSITIVE_ACTION:
            if not approval_token:
                return {
                    "error": f"Tool '{tool_name}' requires explicit approval",
                    "tool_tier": tier.value,
                    "approval_required": True
                }
        
        # Execute tool
        try:
            result = await fn(merchant_id, input_data)
            
            # Log action
            self._log_action(merchant_id, tool_name, tier, input_data, result, "executed", approval_token)
            
            return result
        except Exception as e:
            error_result = {"error": str(e), "tool": tool_name}
            self._log_action(merchant_id, tool_name, tier, input_data, error_result, "failed", approval_token)
            return error_result
    
    # READ tier tools
    async def get_revenue(self, merchant_id: str, input_data: Dict) -> Dict:
        """Get revenue analytics"""
        from app.analytics import AnalyticsEngine
        days = input_data.get("days", 7)
        return AnalyticsEngine.get_revenue(self.db, merchant_id, days)
    
    async def get_transactions(self, merchant_id: str, input_data: Dict) -> Dict:
        """Get transactions"""
        from app.analytics import AnalyticsEngine
        days = input_data.get("days", 7)
        status = input_data.get("status")
        return AnalyticsEngine.get_transactions(self.db, merchant_id, days, status)
    
    async def get_failed_payments(self, merchant_id: str, input_data: Dict) -> Dict:
        """Get failed payments"""
        from app.analytics import AnalyticsEngine
        days = input_data.get("days", 7)
        return AnalyticsEngine.get_failed_payments(self.db, merchant_id, days)
    
    async def get_customers(self, merchant_id: str, input_data: Dict) -> Dict:
        """Get customer statistics"""
        from app.analytics import AnalyticsEngine
        return AnalyticsEngine.get_customers(self.db, merchant_id)
    
    async def get_customer_history(self, merchant_id: str, input_data: Dict) -> Dict:
        """Get customer history"""
        from app.analytics import AnalyticsEngine
        customer_id = input_data.get("customer_id")
        days = input_data.get("days", 90)
        if not customer_id:
            return {"error": "customer_id required"}
        return AnalyticsEngine.get_customer_history(self.db, merchant_id, customer_id, days)
    
    async def get_refunds(self, merchant_id: str, input_data: Dict) -> Dict:
        """Get refunds"""
        from app.analytics import AnalyticsEngine
        days = input_data.get("days", 7)
        return AnalyticsEngine.get_refunds(self.db, merchant_id, days)
    
    async def detect_anomalies(self, merchant_id: str, input_data: Dict) -> Dict:
        """Detect anomalies"""
        from app.analytics import AnalyticsEngine
        baseline_days = input_data.get("baseline_days", 7)
        return AnalyticsEngine.detect_anomalies(self.db, merchant_id, baseline_days)
    
    async def get_top_leaks(self, merchant_id: str, input_data: Dict) -> Dict:
        """Get top revenue leaks"""
        from app.analytics import AnalyticsEngine
        limit = input_data.get("limit", 10)
        return AnalyticsEngine.get_top_revenue_leaks(self.db, merchant_id, limit)
    
    # ANALYZE tier tools
    async def calculate_revenue_loss(self, merchant_id: str, input_data: Dict) -> Dict:
        """Calculate revenue loss"""
        from app.analytics import AnalyticsEngine
        days = input_data.get("days", 7)
        return AnalyticsEngine.calculate_revenue_loss(self.db, merchant_id, days)
    
    async def calculate_revenue_at_risk(self, merchant_id: str, input_data: Dict) -> Dict:
        """Calculate revenue at risk"""
        from app.analytics import AnalyticsEngine
        days = input_data.get("days", 7)
        return AnalyticsEngine.calculate_revenue_at_risk(self.db, merchant_id, days)
    
    async def predict_recovery_probability(self, merchant_id: str, input_data: Dict) -> Dict:
        """Predict recovery probability"""
        from app.analytics import AnalyticsEngine
        transaction_id = input_data.get("transaction_id")
        if not transaction_id:
            return {"error": "transaction_id required"}
        return AnalyticsEngine.predict_recovery_probability(self.db, transaction_id)
    
    async def segment_customers(self, merchant_id: str, input_data: Dict) -> Dict:
        """Segment customers"""
        from app.analytics import AnalyticsEngine
        return AnalyticsEngine.segment_customers(self.db, merchant_id)
    
    async def analyze_payment_methods(self, merchant_id: str, input_data: Dict) -> Dict:
        """Analyze by payment method"""
        from app.analytics import AnalyticsEngine
        days = input_data.get("days", 7)
        
        methods = {}
        for method in ["card", "upi", "netbanking", "wallet"]:
            result = AnalyticsEngine.get_payment_success_rate(self.db, merchant_id, days, method)
            methods[method] = result
        
        return {"by_method": methods}
    
    # RECOMMEND tier tools
    async def recommend_recovery_campaign(self, merchant_id: str, input_data: Dict) -> Dict:
        """Recommend recovery campaign"""
        target_count = input_data.get("target_count", 10)
        
        from app.analytics import AnalyticsEngine
        leaks = AnalyticsEngine.get_top_revenue_leaks(self.db, merchant_id, target_count)
        
        return {
            "campaign_type": "recovery",
            "target_customers": target_count,
            "total_potential_recovery": leaks.get("total_recovery_potential", 0),
            "recommended_leaks": leaks.get("top_leaks", []),
            "recommendation": f"Send recovery messages to {target_count} customers with highest recovery potential",
        }
    
    # LOW_RISK_ACTION tier tools
    async def create_payment_link(self, merchant_id: str, input_data: Dict) -> Dict:
        """Create a payment link for recovery"""
        customer_email = input_data.get("customer_email")
        amount = input_data.get("amount")
        description = input_data.get("description", "Payment recovery link")
        
        if not customer_email or not amount:
            return {"error": "customer_email and amount required"}
        
        return self.provider.create_payment_link(float(amount), customer_email, description)
    
    async def send_recovery_message(self, merchant_id: str, input_data: Dict) -> Dict:
        """Send recovery message to customer"""
        customer_id = input_data.get("customer_id")
        message = input_data.get("message", "We'd like to help you complete your payment.")
        
        if not customer_id:
            return {"error": "customer_id required"}
        
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return {"error": "Customer not found"}
        
        return {
            "status": "sent",
            "customer_id": customer_id,
            "customer_email": customer.email,
            "message": message,
            "sent_at": datetime.utcnow().isoformat(),
            "note": "Mock message. In production, integrate with email/SMS service."
        }
    
    async def get_campaign_results(self, merchant_id: str, input_data: Dict) -> Dict:
        """Get results of a recovery campaign"""
        campaign_id = input_data.get("campaign_id")
        
        if not campaign_id:
            return {"error": "campaign_id required"}
        
        return {
            "campaign_id": campaign_id,
            "sent": 10,
            "completed": 3,
            "completion_rate": 0.30,
            "total_recovered": 15000.0,
            "note": "Mock results. In production, fetch from campaign tracking system."
        }
    
    # SENSITIVE_ACTION tier tools
    async def refund_payment(self, merchant_id: str, input_data: Dict) -> Dict:
        """Refund a payment (REQUIRES APPROVAL)"""
        payment_id = input_data.get("payment_id")
        amount = input_data.get("amount")
        reason = input_data.get("reason", "Customer request")
        
        if not payment_id or not amount:
            return {"error": "payment_id and amount required"}
        
        result = self.provider.refund_payment(payment_id, float(amount), reason)
        result["approval_required"] = True
        return result
    
    async def bulk_customer_campaign(self, merchant_id: str, input_data: Dict) -> Dict:
        """Launch bulk campaign to multiple customers (REQUIRES APPROVAL)"""
        customer_ids = input_data.get("customer_ids", [])
        campaign_type = input_data.get("campaign_type", "recovery")
        message = input_data.get("message", "")
        
        if not customer_ids:
            return {"error": "customer_ids required"}
        
        return {
            "campaign_id": str(uuid.uuid4()),
            "type": campaign_type,
            "target_count": len(customer_ids),
            "status": "pending_approval",
            "approval_required": True,
            "note": "Bulk campaign pending approval"
        }
    
    async def create_payout(self, merchant_id: str, input_data: Dict) -> Dict:
        """Create a payout (REQUIRES APPROVAL)"""
        account_number = input_data.get("account_number")
        amount = input_data.get("amount")
        description = input_data.get("description", "Payout")
        
        if not account_number or not amount:
            return {"error": "account_number and amount required"}
        
        result = self.provider.create_payout(account_number, float(amount), description)
        result["approval_required"] = True
        return result
    
    def _log_action(self, merchant_id: str, tool_name: str, tier: ActionTier, 
                    input_data: Dict, result: Dict, status: str, approval_token: Optional[str] = None):
        """Log action to database"""
        try:
            action = AgentAction(
                id=str(uuid.uuid4()),
                merchant_id=merchant_id,
                agent="revpilot",
                action=tool_name,
                tool=tool_name,
                tool_tier=tier,
                input_data=json.dumps(input_data),
                result=json.dumps(result),
                status=ActionStatus.EXECUTED if status == "executed" else ActionStatus.FAILED,
                approval=approval_token or f"auto_approved_{tier.value}",
                created_at=datetime.utcnow(),
            )
            self.db.add(action)
            self.db.commit()
        except:
            pass  # Fail silently, don't break action execution
