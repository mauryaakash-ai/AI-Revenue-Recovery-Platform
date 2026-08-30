"""
Agent orchestration for RevPilot.
Coordinates investigation → root cause → recommendation → approval → action → measurement.
"""

import asyncio
import json
from typing import Dict, Optional, AsyncGenerator
from datetime import datetime
from sqlalchemy.orm import Session
from app.analytics import AnalyticsEngine
from app.tools import ToolRegistry
from app.providers import ProviderFactory


class RevPilotAgent:
    """The main revenue intelligence agent"""
    
    def __init__(self, db: Session, merchant_id: str, provider_name: str = "mock"):
        self.db = db
        self.merchant_id = merchant_id
        self.provider = ProviderFactory.get_default_provider() if provider_name == "mock" else ProviderFactory.create(provider_name)
        self.tools = ToolRegistry(db, self.provider)
        self.investigation_steps = []
    
    async def investigate(self, query: str) -> AsyncGenerator[str, None]:
        """
        Main agent loop: investigate query end-to-end.
        Yields JSON objects with step updates for real-time frontend display.
        """
        
        step_num = 0
        
        try:
            # Step 1: Intent detection
            step_num += 1
            yield json.dumps({
                "step": step_num,
                "status": "in_progress",
                "phase": "intent_detection",
                "message": f"Understanding your query: '{query}'",
                "timestamp": datetime.utcnow().isoformat()
            }) + "\n"
            
            intent = await self._detect_intent(query)
            yield json.dumps({
                "step": step_num,
                "status": "complete",
                "phase": "intent_detection",
                "message": f"Intent: {intent.get('type')}",
                "details": intent,
                "timestamp": datetime.utcnow().isoformat()
            }) + "\n"
            
            # Step 2: Investigation planning
            step_num += 1
            yield json.dumps({
                "step": step_num,
                "status": "in_progress",
                "phase": "investigation_planning",
                "message": "Planning investigation...",
                "timestamp": datetime.utcnow().isoformat()
            }) + "\n"
            
            plan = await self._create_investigation_plan(intent)
            yield json.dumps({
                "step": step_num,
                "status": "complete",
                "phase": "investigation_planning",
                "message": f"Planned {len(plan.get('steps', []))} investigation steps",
                "details": plan,
                "timestamp": datetime.utcnow().isoformat()
            }) + "\n"
            
            # Step 3: Execute investigation
            step_num += 1
            yield json.dumps({
                "step": step_num,
                "status": "in_progress",
                "phase": "investigation_execution",
                "message": "Executing investigation...",
                "timestamp": datetime.utcnow().isoformat()
            }) + "\n"
            
            investigation_results = {}
            for plan_step in plan.get("steps", []):
                tool_name = plan_step.get("tool")
                tool_input = plan_step.get("input", {})
                
                yield json.dumps({
                    "step": step_num,
                    "status": "in_progress",
                    "phase": "investigation_execution",
                    "message": f"Executing: {tool_name}",
                    "current_tool": tool_name,
                    "timestamp": datetime.utcnow().isoformat()
                }) + "\n"
                
                result = await self.tools.execute_tool(tool_name, self.merchant_id, tool_input)
                investigation_results[tool_name] = result
            
            yield json.dumps({
                "step": step_num,
                "status": "complete",
                "phase": "investigation_execution",
                "message": "Investigation complete",
                "results_collected": len(investigation_results),
                "timestamp": datetime.utcnow().isoformat()
            }) + "\n"
            
            # Step 4: Root cause analysis
            step_num += 1
            yield json.dumps({
                "step": step_num,
                "status": "in_progress",
                "phase": "root_cause_analysis",
                "message": "Analyzing root causes...",
                "timestamp": datetime.utcnow().isoformat()
            }) + "\n"
            
            root_causes = await self._analyze_root_causes(intent, investigation_results)
            yield json.dumps({
                "step": step_num,
                "status": "complete",
                "phase": "root_cause_analysis",
                "message": f"Identified {len(root_causes)} root cause(s)",
                "details": root_causes,
                "timestamp": datetime.utcnow().isoformat()
            }) + "\n"
            
            # Step 5: Financial impact calculation
            step_num += 1
            yield json.dumps({
                "step": step_num,
                "status": "in_progress",
                "phase": "financial_impact",
                "message": "Calculating financial impact...",
                "timestamp": datetime.utcnow().isoformat()
            }) + "\n"
            
            impact = await self._calculate_financial_impact(investigation_results, root_causes)
            yield json.dumps({
                "step": step_num,
                "status": "complete",
                "phase": "financial_impact",
                "message": f"Impact: ₹{impact.get('total_impact', 0):.0f}",
                "details": impact,
                "timestamp": datetime.utcnow().isoformat()
            }) + "\n"
            
            # Step 6: Ranking recovery opportunities
            step_num += 1
            yield json.dumps({
                "step": step_num,
                "status": "in_progress",
                "phase": "prioritization",
                "message": "Ranking recovery opportunities...",
                "timestamp": datetime.utcnow().isoformat()
            }) + "\n"
            
            ranked_opportunities = await self._rank_opportunities(investigation_results)
            yield json.dumps({
                "step": step_num,
                "status": "complete",
                "phase": "prioritization",
                "message": f"Ranked {len(ranked_opportunities)} recovery opportunities",
                "details": {"opportunities": ranked_opportunities[:5]},  # Top 5
                "timestamp": datetime.utcnow().isoformat()
            }) + "\n"
            
            # Step 7: Recommendation
            step_num += 1
            yield json.dumps({
                "step": step_num,
                "status": "in_progress",
                "phase": "recommendation",
                "message": "Generating recommendation...",
                "timestamp": datetime.utcnow().isoformat()
            }) + "\n"
            
            recommendation = await self._generate_recommendation(intent, impact, ranked_opportunities)
            yield json.dumps({
                "step": step_num,
                "status": "complete",
                "phase": "recommendation",
                "message": recommendation.get("summary", ""),
                "details": recommendation,
                "timestamp": datetime.utcnow().isoformat()
            }) + "\n"
            
            # Step 8: Summary
            step_num += 1
            yield json.dumps({
                "step": step_num,
                "status": "complete",
                "phase": "complete",
                "message": "Investigation complete - awaiting approval",
                "summary": {
                    "intent": intent,
                    "root_causes": root_causes,
                    "impact": impact,
                    "recommendation": recommendation,
                },
                "timestamp": datetime.utcnow().isoformat()
            }) + "\n"
        
        except Exception as e:
            yield json.dumps({
                "step": step_num,
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }) + "\n"
    
    async def _detect_intent(self, query: str) -> Dict:
        """Detect intent from natural language query"""
        query_lower = query.lower()
        
        intent_type = "general_inquiry"
        
        if any(word in query_lower for word in ["why", "reason", "cause", "drop", "down", "low"]):
            intent_type = "anomaly_investigation"
        elif any(word in query_lower for word in ["recover", "recovery", "revenue", "lost", "fail", "fail"]):
            intent_type = "recovery_planning"
        elif any(word in query_lower for word in ["customer", "segment", "cohort"]):
            intent_type = "customer_analysis"
        elif any(word in query_lower for word in ["refund", "chargeback", "dispute"]):
            intent_type = "refund_analysis"
        
        return {
            "type": intent_type,
            "query": query,
            "confidence": 0.85
        }
    
    async def _create_investigation_plan(self, intent: Dict) -> Dict:
        """Create investigation plan based on intent"""
        intent_type = intent.get("type", "general_inquiry")
        
        plans = {
            "anomaly_investigation": [
                {"tool": "detect_anomalies", "input": {"baseline_days": 7}},
                {"tool": "get_revenue", "input": {"days": 7}},
                {"tool": "get_failed_payments", "input": {"days": 7}},
                {"tool": "analyze_payment_methods", "input": {"days": 7}},
                {"tool": "calculate_revenue_loss", "input": {"days": 7}},
            ],
            "recovery_planning": [
                {"tool": "get_top_leaks", "input": {"limit": 20}},
                {"tool": "calculate_revenue_at_risk", "input": {"days": 7}},
                {"tool": "get_customers", "input": {}},
                {"tool": "recommend_recovery_campaign", "input": {"target_count": 10}},
            ],
            "customer_analysis": [
                {"tool": "get_customers", "input": {}},
                {"tool": "segment_customers", "input": {}},
            ],
            "refund_analysis": [
                {"tool": "get_refunds", "input": {"days": 7}},
                {"tool": "get_failed_payments", "input": {"days": 7}},
            ],
            "general_inquiry": [
                {"tool": "get_revenue", "input": {"days": 7}},
                {"tool": "get_transactions", "input": {"days": 7}},
                {"tool": "detect_anomalies", "input": {"baseline_days": 7}},
            ]
        }
        
        steps = plans.get(intent_type, plans["general_inquiry"])
        
        return {
            "intent": intent_type,
            "steps": steps,
            "total_steps": len(steps)
        }
    
    async def _analyze_root_causes(self, intent: Dict, results: Dict) -> list:
        """Analyze root causes from investigation results"""
        causes = []
        
        if "get_failed_payments" in results:
            failed = results["get_failed_payments"]
            if failed.get("total_failed", 0) > 5:
                causes.append({
                    "category": "payment_failures",
                    "description": f"{failed.get('total_failed', 0)} failed transactions",
                    "impact_estimate": failed.get("total_failed_amount", 0),
                    "confidence": 0.95
                })
        
        if "detect_anomalies" in results:
            anomalies = results["detect_anomalies"]
            if anomalies.get("has_anomaly"):
                causes.append({
                    "category": "revenue_anomaly",
                    "description": f"Revenue deviation: {anomalies['revenue'].get('deviation_pct', 0):.1f}%",
                    "impact_estimate": abs(anomalies['revenue'].get('today', 0) - anomalies['revenue'].get('baseline_avg', 0)),
                    "confidence": anomalies.get("confidence", 0.5)
                })
        
        if "analyze_payment_methods" in results:
            by_method = results["analyze_payment_methods"].get("by_method", {})
            for method, data in by_method.items():
                if data.get("success_rate", 100) < 85:
                    causes.append({
                        "category": "method_degradation",
                        "description": f"{method} success rate: {data.get('success_rate', 0):.1f}%",
                        "impact_estimate": data.get("failed", 0) * 5000,  # Rough estimate
                        "confidence": 0.70
                    })
        
        return causes
    
    async def _calculate_financial_impact(self, results: Dict, root_causes: list) -> Dict:
        """Calculate total financial impact"""
        total_impact = 0.0
        total_at_risk = 0.0
        total_recoverable = 0.0
        
        if "calculate_revenue_loss" in results:
            total_impact += results["calculate_revenue_loss"].get("revenue_lost", 0)
        
        if "calculate_revenue_at_risk" in results:
            total_at_risk = results["calculate_revenue_at_risk"].get("total_at_risk", 0)
            total_recoverable = total_at_risk * 0.4  # 40% recovery assumption
        
        return {
            "total_impact": float(total_impact),
            "at_risk": float(total_at_risk),
            "recoverable_estimate": float(total_recoverable),
            "estimate_type": "conservative",
            "confidence": 0.75
        }
    
    async def _rank_opportunities(self, results: Dict) -> list:
        """Rank recovery opportunities"""
        opportunities = []
        
        if "get_top_leaks" in results:
            leaks = results["get_top_leaks"].get("top_leaks", [])
            for leak in leaks[:10]:
                opportunities.append({
                    "id": leak.get("id"),
                    "type": leak.get("type"),
                    "amount": leak.get("amount"),
                    "recovery_potential": leak.get("expected_recovery"),
                    "priority_score": self._calculate_priority_score(leak),
                })
        
        # Sort by priority score
        opportunities.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return opportunities
    
    def _calculate_priority_score(self, opportunity: Dict) -> float:
        """Calculate priority score for an opportunity"""
        from app.analytics import AnalyticsEngine
        recovery_potential = opportunity.get("recovery_potential", 0)
        probability = opportunity.get("recovery_probability", 0.5)
        
        return AnalyticsEngine.priority_score(recovery_potential, probability, urgency=1.0, confidence=0.8)
    
    async def _generate_recommendation(self, intent: Dict, impact: Dict, opportunities: list) -> Dict:
        """Generate recommendation for merchant"""
        total_recovery = impact.get("recoverable_estimate", 0)
        num_opportunities = len(opportunities)
        
        recommendation = {
            "summary": f"We identified ₹{impact.get('total_impact', 0):.0f} in immediate revenue loss and up to ₹{total_recovery:.0f} in recoverable revenue from {num_opportunities} high-priority customers.",
            "recommendation": f"Send personalized recovery messages to the top 10 customers with payment link offers. Expected recovery: ₹{total_recovery * 0.3:.0f}.",
            "next_steps": [
                "Review the top recovery candidates below",
                "Click 'Approve' to send recovery campaigns",
                "Monitor campaign results in real-time"
            ],
            "confidence": 0.80,
            "top_candidates": opportunities[:5]
        }
        
        return recommendation
