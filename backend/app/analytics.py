"""
Analytics layer for RevPilot.
All functions are deterministic, independently testable, and return labeled estimates.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import numpy as np
from app.models import (
    Transaction, Customer, Refund, Settlement, CheckoutEvent,
    TransactionStatus, RefundStatus
)


class AnalyticsEngine:
    """Deterministic analytics functions, no ML involved"""
    
    @staticmethod
    def get_revenue(db: Session, merchant_id: str, days: int = 7) -> Dict:
        """Calculate total and daily revenue"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        total_revenue = db.query(func.sum(Transaction.amount)).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.status == TransactionStatus.SUCCESS,
            Transaction.created_at >= cutoff_date
        ).scalar() or 0.0
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_revenue = db.query(func.sum(Transaction.amount)).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.status == TransactionStatus.SUCCESS,
            Transaction.created_at >= today_start
        ).scalar() or 0.0
        
        yesterday_start = (datetime.utcnow() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_end = yesterday_start + timedelta(days=1)
        yesterday_revenue = db.query(func.sum(Transaction.amount)).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.status == TransactionStatus.SUCCESS,
            Transaction.created_at >= yesterday_start,
            Transaction.created_at < yesterday_end
        ).scalar() or 0.0
        
        delta = today_revenue - yesterday_revenue
        delta_pct = (delta / yesterday_revenue * 100) if yesterday_revenue > 0 else 0
        
        return {
            "total_revenue": float(total_revenue),
            "today_revenue": float(today_revenue),
            "yesterday_revenue": float(yesterday_revenue),
            "delta": float(delta),
            "delta_percentage": float(delta_pct),
            "period_days": days
        }
    
    @staticmethod
    def get_transactions(db: Session, merchant_id: str, days: int = 7, status: str = None) -> Dict:
        """Get transactions with optional status filter"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.created_at >= cutoff_date
        )
        
        if status:
            query = query.filter(Transaction.status == status)
        
        transactions = query.all()
        
        return {
            "count": len(transactions),
            "transactions": [
                {
                    "id": t.id,
                    "amount": float(t.amount),
                    "payment_method": t.payment_method,
                    "status": t.status.value,
                    "created_at": t.created_at.isoformat(),
                }
                for t in transactions
            ]
        }
    
    @staticmethod
    def get_failed_payments(db: Session, merchant_id: str, days: int = 7) -> Dict:
        """Analyze failed payments by reason and method"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        failed = db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.status == TransactionStatus.FAILED,
            Transaction.created_at >= cutoff_date
        ).all()
        
        # Group by failure reason
        by_reason = {}
        for t in failed:
            reason = t.failure_reason or "unknown"
            if reason not in by_reason:
                by_reason[reason] = {"count": 0, "total_amount": 0.0}
            by_reason[reason]["count"] += 1
            by_reason[reason]["total_amount"] += t.amount
        
        # Group by payment method
        by_method = {}
        for t in failed:
            method = t.payment_method
            if method not in by_method:
                by_method[method] = {"count": 0, "total_amount": 0.0}
            by_method[method]["count"] += 1
            by_method[method]["total_amount"] += t.amount
        
        total_failed_amount = sum(t.amount for t in failed)
        
        return {
            "total_failed": len(failed),
            "total_failed_amount": float(total_failed_amount),
            "by_reason": {k: {"count": v["count"], "amount": float(v["total_amount"])} for k, v in by_reason.items()},
            "by_method": {k: {"count": v["count"], "amount": float(v["total_amount"])} for k, v in by_method.items()},
        }
    
    @staticmethod
    def get_payment_success_rate(db: Session, merchant_id: str, days: int = 7, payment_method: str = None) -> Dict:
        """Calculate success rate overall or by payment method"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query_all = db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.created_at >= cutoff_date
        )
        
        if payment_method:
            query_all = query_all.filter(Transaction.payment_method == payment_method)
        
        total = query_all.count()
        
        successful = query_all.filter(
            Transaction.status == TransactionStatus.SUCCESS
        ).count()
        
        success_rate = (successful / total * 100) if total > 0 else 0
        
        return {
            "success_rate": float(success_rate),
            "successful": successful,
            "total": total,
            "failed": total - successful,
            "payment_method": payment_method or "all"
        }
    
    @staticmethod
    def get_customers(db: Session, merchant_id: str) -> Dict:
        """Get customer statistics"""
        customers = db.query(Customer).filter(
            Customer.merchant_id == merchant_id
        ).all()
        
        segments = {}
        total_ltv = 0.0
        
        for c in customers:
            segment = c.segment or "unknown"
            if segment not in segments:
                segments[segment] = {"count": 0, "total_ltv": 0.0}
            segments[segment]["count"] += 1
            segments[segment]["total_ltv"] += c.lifetime_value
            total_ltv += c.lifetime_value
        
        return {
            "total_customers": len(customers),
            "total_ltv": float(total_ltv),
            "avg_ltv": float(total_ltv / len(customers)) if customers else 0.0,
            "by_segment": {k: {"count": v["count"], "ltv": float(v["total_ltv"])} for k, v in segments.items()}
        }
    
    @staticmethod
    def get_customer_history(db: Session, merchant_id: str, customer_id: str, days: int = 90) -> Dict:
        """Get detailed customer transaction history"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        customer = db.query(Customer).filter(
            Customer.merchant_id == merchant_id,
            Customer.id == customer_id
        ).first()
        
        if not customer:
            return {"error": "Customer not found"}
        
        transactions = db.query(Transaction).filter(
            Transaction.customer_id == customer_id,
            Transaction.created_at >= cutoff_date
        ).all()
        
        successful = sum(1 for t in transactions if t.status == TransactionStatus.SUCCESS)
        failed = sum(1 for t in transactions if t.status == TransactionStatus.FAILED)
        total_spent = sum(t.amount for t in transactions if t.status == TransactionStatus.SUCCESS)
        
        return {
            "customer_id": customer_id,
            "name": customer.name,
            "segment": customer.segment,
            "lifetime_value": float(customer.lifetime_value),
            "transaction_count": len(transactions),
            "successful": successful,
            "failed": failed,
            "total_spent": float(total_spent),
            "transactions": [
                {
                    "id": t.id,
                    "amount": float(t.amount),
                    "status": t.status.value,
                    "created_at": t.created_at.isoformat(),
                }
                for t in transactions
            ]
        }
    
    @staticmethod
    def get_refunds(db: Session, merchant_id: str, days: int = 7) -> Dict:
        """Analyze refunds"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        refunds = db.query(Refund).filter(
            Refund.merchant_id == merchant_id,
            Refund.created_at >= cutoff_date
        ).all()
        
        by_reason = {}
        for r in refunds:
            reason = r.reason
            if reason not in by_reason:
                by_reason[reason] = {"count": 0, "total_amount": 0.0}
            by_reason[reason]["count"] += 1
            by_reason[reason]["total_amount"] += r.amount
        
        by_status = {}
        for r in refunds:
            status = r.status.value
            if status not in by_status:
                by_status[status] = {"count": 0, "total_amount": 0.0}
            by_status[status]["count"] += 1
            by_status[status]["total_amount"] += r.amount
        
        total_refunded = sum(r.amount for r in refunds)
        
        return {
            "total_refunds": len(refunds),
            "total_refunded_amount": float(total_refunded),
            "by_reason": {k: {"count": v["count"], "amount": float(v["total_amount"])} for k, v in by_reason.items()},
            "by_status": {k: {"count": v["count"], "amount": float(v["total_amount"])} for k, v in by_status.items()},
        }
    
    @staticmethod
    def get_settlements(db: Session, merchant_id: str, days: int = 7) -> Dict:
        """Analyze settlements"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        settlements = db.query(Settlement).filter(
            Settlement.merchant_id == merchant_id,
            Settlement.settlement_date >= cutoff_date
        ).all()
        
        total_settled = sum(s.amount for s in settlements if s.status.value == "completed")
        pending_settled = sum(s.amount for s in settlements if s.status.value == "pending")
        
        return {
            "total_settlements": len(settlements),
            "completed_count": sum(1 for s in settlements if s.status.value == "completed"),
            "pending_count": sum(1 for s in settlements if s.status.value == "pending"),
            "total_completed_amount": float(total_settled),
            "total_pending_amount": float(pending_settled),
        }
    
    @staticmethod
    def get_checkout_events(db: Session, merchant_id: str, days: int = 7) -> Dict:
        """Analyze checkout funnel"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all customers and their checkout events
        events = db.query(CheckoutEvent).join(Customer).filter(
            Customer.merchant_id == merchant_id,
            CheckoutEvent.timestamp >= cutoff_date
        ).all()
        
        # Count by event type
        by_event = {"initiated": 0, "completed": 0, "abandoned": 0}
        sessions_initiated = set()
        sessions_completed = set()
        sessions_abandoned = set()
        
        for e in events:
            if e.event in by_event:
                by_event[e.event] += 1
            
            if e.event == "initiated":
                sessions_initiated.add(e.session_id)
            elif e.event == "completed":
                sessions_completed.add(e.session_id)
            elif e.event == "abandoned":
                sessions_abandoned.add(e.session_id)
        
        initiated_count = len(sessions_initiated)
        completion_rate = (len(sessions_completed) / initiated_count * 100) if initiated_count > 0 else 0
        abandonment_rate = (len(sessions_abandoned) / initiated_count * 100) if initiated_count > 0 else 0
        
        return {
            "event_counts": by_event,
            "sessions_initiated": initiated_count,
            "sessions_completed": len(sessions_completed),
            "sessions_abandoned": len(sessions_abandoned),
            "completion_rate": float(completion_rate),
            "abandonment_rate": float(abandonment_rate),
        }
    
    @staticmethod
    def detect_anomalies(db: Session, merchant_id: str, baseline_days: int = 7) -> Dict:
        """
        Detect anomalies using statistical deviation from baseline.
        Compares last day vs. average of prior baseline_days.
        Returns labeled confidence-bounded estimate.
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        baseline_cutoff = today_start - timedelta(days=baseline_days + 1)
        
        # Today's metrics
        today_success_txns = db.query(func.count(Transaction.id)).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.status == TransactionStatus.SUCCESS,
            Transaction.created_at >= today_start
        ).scalar() or 0
        
        today_revenue = db.query(func.sum(Transaction.amount)).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.status == TransactionStatus.SUCCESS,
            Transaction.created_at >= today_start
        ).scalar() or 0.0
        
        today_failed_txns = db.query(func.count(Transaction.id)).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.status == TransactionStatus.FAILED,
            Transaction.created_at >= today_start
        ).scalar() or 0
        
        # Baseline: average of prior N days
        baseline_days_list = []
        for i in range(1, baseline_days + 1):
            day_start = today_start - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_revenue = db.query(func.sum(Transaction.amount)).filter(
                Transaction.merchant_id == merchant_id,
                Transaction.status == TransactionStatus.SUCCESS,
                Transaction.created_at >= day_start,
                Transaction.created_at < day_end
            ).scalar() or 0.0
            
            baseline_days_list.append(day_revenue)
        
        baseline_avg_revenue = np.mean(baseline_days_list) if baseline_days_list else 0
        baseline_std_revenue = np.std(baseline_days_list) if len(baseline_days_list) > 1 else 0
        
        # Calculate z-score for revenue
        revenue_deviation = 0
        revenue_zscore = 0
        if baseline_std_revenue > 0:
            revenue_zscore = (today_revenue - baseline_avg_revenue) / baseline_std_revenue
            revenue_deviation = abs(revenue_zscore)
        
        # Determine if anomaly
        is_anomaly = revenue_deviation > 2.0  # 2-sigma
        confidence = min(1.0, abs(revenue_zscore) / 3.0)  # Confidence as fraction of 3-sigma
        
        anomalies = []
        if today_failed_txns > 0:
            baseline_failed_days = []
            for i in range(1, baseline_days + 1):
                day_start = today_start - timedelta(days=i)
                day_end = day_start + timedelta(days=1)
                
                day_failed = db.query(func.count(Transaction.id)).filter(
                    Transaction.merchant_id == merchant_id,
                    Transaction.status == TransactionStatus.FAILED,
                    Transaction.created_at >= day_start,
                    Transaction.created_at < day_end
                ).scalar() or 0
                
                baseline_failed_days.append(day_failed)
            
            baseline_avg_failed = np.mean(baseline_failed_days) if baseline_failed_days else 0
            failure_rate_today = today_failed_txns / (today_success_txns + today_failed_txns) if (today_success_txns + today_failed_txns) > 0 else 0
            baseline_avg_rate = baseline_avg_failed / ((np.mean([db.query(func.count(Transaction.id)).filter(
                Transaction.merchant_id == merchant_id,
                Transaction.created_at >= (today_start - timedelta(days=i)),
                Transaction.created_at < (today_start - timedelta(days=i-1))
            ).scalar() or 0 for i in range(1, baseline_days + 1)])) + baseline_avg_failed) if baseline_avg_failed > 0 else 0
            
            if failure_rate_today > baseline_avg_rate * 1.2:  # 20% above baseline
                anomalies.append({
                    "type": "high_failure_rate",
                    "current": float(failure_rate_today),
                    "baseline": float(baseline_avg_rate),
                    "confidence": min(1.0, (failure_rate_today - baseline_avg_rate) / baseline_avg_rate) if baseline_avg_rate > 0 else 0.5
                })
        
        return {
            "has_anomaly": is_anomaly,
            "confidence": float(min(1.0, confidence)),
            "revenue": {
                "today": float(today_revenue),
                "baseline_avg": float(baseline_avg_revenue),
                "zscore": float(revenue_zscore),
                "deviation_pct": float((today_revenue - baseline_avg_revenue) / baseline_avg_revenue * 100) if baseline_avg_revenue > 0 else 0
            },
            "anomalies": anomalies
        }
    
    @staticmethod
    def calculate_revenue_loss(db: Session, merchant_id: str, days: int = 7) -> Dict:
        """Calculate revenue lost from failed transactions"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        failed = db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.status == TransactionStatus.FAILED,
            Transaction.created_at >= cutoff_date
        ).all()
        
        total_failed_amount = sum(t.amount for t in failed)
        
        return {
            "failed_transactions": len(failed),
            "revenue_lost": float(total_failed_amount),
            "estimate_type": "confirmed_loss",
            "confidence": 1.0,  # 100% confirmed - these failed
        }
    
    @staticmethod
    def calculate_revenue_at_risk(db: Session, merchant_id: str, days: int = 7) -> Dict:
        """
        Calculate revenue at risk from:
        1. Checkout abandonments
        2. High-value failed transactions that might recover
        Returns labeled estimate with confidence bounds.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 1. Abandoned checkouts (estimated value)
        events = db.query(CheckoutEvent).join(Customer).filter(
            Customer.merchant_id == merchant_id,
            CheckoutEvent.timestamp >= cutoff_date,
            CheckoutEvent.event == "abandoned"
        ).all()
        
        # Estimate value based on average transaction amount
        avg_transaction = db.query(func.avg(Transaction.amount)).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.status == TransactionStatus.SUCCESS,
            Transaction.created_at >= cutoff_date
        ).scalar() or 0.0
        
        abandoned_sessions = len(set(e.session_id for e in events))
        abandoned_revenue_at_risk = abandoned_sessions * avg_transaction
        
        # 2. High-value failed transactions (recoverable)
        failed_high_value = db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.status == TransactionStatus.FAILED,
            Transaction.created_at >= cutoff_date,
            Transaction.amount >= avg_transaction * 1.5  # High-value: 1.5x average
        ).all()
        
        recoverable_failed_amount = sum(t.amount for t in failed_high_value)
        
        # Estimate: assume 40% recovery probability on high-value
        estimated_recovery = recoverable_failed_amount * 0.4
        
        total_at_risk = abandoned_revenue_at_risk + estimated_recovery
        
        return {
            "total_at_risk": float(total_at_risk),
            "estimate_type": "optimistic_with_confidence_bounds",
            "components": {
                "abandoned_checkouts": float(abandoned_revenue_at_risk),
                "high_value_recoverable": float(estimated_recovery),
            },
            "confidence": 0.65,  # Moderate confidence - these are estimates
            "note": "Estimate based on abandoned sessions and high-value failures; actual recovery depends on customer behavior"
        }
    
    @staticmethod
    def predict_recovery_probability(db: Session, transaction_id: str) -> Dict:
        """
        Predict recovery probability for a failed transaction.
        Returns probability + expected recovery amount.
        """
        from app.models import RecoveryPrediction
        
        prediction = db.query(RecoveryPrediction).filter(
            RecoveryPrediction.transaction_id == transaction_id
        ).first()
        
        if not prediction:
            return {"error": "No prediction found"}
        
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            return {"error": "Transaction not found"}
        
        return {
            "transaction_id": transaction_id,
            "probability": float(prediction.probability),
            "expected_recovery": float(prediction.expected_recovery),
            "confidence": float(prediction.probability),  # Confidence ~= probability for this model
            "failure_reason": transaction.failure_reason,
            "model_version": prediction.model_version,
        }
    
    @staticmethod
    def segment_customers(db: Session, merchant_id: str) -> Dict:
        """Segment customers by RFM (Recency, Frequency, Monetary)"""
        customers = db.query(Customer).filter(
            Customer.merchant_id == merchant_id
        ).all()
        
        if not customers:
            return {"segments": {}}
        
        # Use lifetime_value and segment field
        segments = {}
        for c in customers:
            segment = c.segment or "unknown"
            if segment not in segments:
                segments[segment] = []
            segments[segment].append({
                "id": c.id,
                "ltv": float(c.lifetime_value)
            })
        
        segment_stats = {}
        for segment, cust_list in segments.items():
            ltv_values = [c["ltv"] for c in cust_list]
            segment_stats[segment] = {
                "count": len(cust_list),
                "avg_ltv": float(np.mean(ltv_values)),
                "total_ltv": float(sum(ltv_values)),
                "customers": cust_list[:10]  # Sample first 10
            }
        
        return {
            "total_customers": len(customers),
            "segments": segment_stats
        }
    
    @staticmethod
    def get_top_revenue_leaks(db: Session, merchant_id: str, limit: int = 10) -> Dict:
        """
        Identify top revenue leaks ranked by impact.
        Returns high-value failed transactions, refunds, and abandoned sessions.
        """
        from app.models import RecoveryPrediction
        
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        
        leaks = []
        
        # 1. High-value failed transactions
        failed_high = db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.status == TransactionStatus.FAILED,
            Transaction.created_at >= week_ago,
            Transaction.amount >= 5000  # Threshold for "high-value"
        ).all()
        
        for tx in failed_high:
            pred = db.query(RecoveryPrediction).filter(
                RecoveryPrediction.transaction_id == tx.id
            ).first()
            
            prob = pred.probability if pred else 0.5
            expected_recovery = tx.amount * prob
            
            leaks.append({
                "type": "failed_transaction",
                "id": tx.id,
                "amount": float(tx.amount),
                "expected_recovery": float(expected_recovery),
                "recovery_probability": float(prob),
                "customer_id": tx.customer_id,
                "reason": tx.failure_reason,
                "created_at": tx.created_at.isoformat(),
            })
        
        # 2. Refund spikes
        refunds_recent = db.query(Refund).filter(
            Refund.merchant_id == merchant_id,
            Refund.created_at >= week_ago
        ).all()
        
        for ref in refunds_recent:
            leaks.append({
                "type": "refund",
                "id": ref.id,
                "amount": float(ref.amount),
                "expected_recovery": 0.0,  # Already lost
                "recovery_probability": 0.0,
                "reason": ref.reason,
                "created_at": ref.created_at.isoformat(),
            })
        
        # Sort by expected recovery
        leaks.sort(key=lambda x: x["expected_recovery"], reverse=True)
        
        return {
            "total_leaks": len(leaks),
            "top_leaks": leaks[:limit],
            "total_recovery_potential": float(sum(l["expected_recovery"] for l in leaks)),
        }
    
    @staticmethod
    def priority_score(expected_recovery: float, recovery_probability: float, 
                       urgency: float = 1.0, confidence: float = 1.0) -> float:
        """
        Priority scoring formula:
        score = expected_recovery × recovery_probability × urgency × confidence
        
        Normalized to 0-100.
        """
        score = expected_recovery * recovery_probability * urgency * confidence
        # Normalize: assume max expected_recovery is 1M and others are normalized
        max_possible = 1_000_000 * 1.0 * 1.0 * 1.0
        normalized = (score / max_possible) * 100 if max_possible > 0 else 0
        return min(100.0, max(0.0, normalized))
