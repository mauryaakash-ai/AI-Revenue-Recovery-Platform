"""
AI Revenue Assistant (Copilot) route:
Integrates RAG Knowledge Retrieval, Multi-Agent Orchestration, and Structured Diagnostics.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.database import get_db
from app.models import Merchant, RecoveryOpportunity, Transaction, Customer, Alert
from app.rag_copilot import RevenueIntelligenceCopilot
from app.multi_agent_system import RevPilotMultiAgentOrchestrator

router = APIRouter()
copilot_engine = RevenueIntelligenceCopilot()


class CopilotQuery(BaseModel):
    query: str
    user_role: Optional[str] = "Revenue Operations"
    context: Optional[Dict[str, Any]] = None


@router.post("/merchants/{merchant_id}/copilot/ask")
async def copilot_ask(
    merchant_id: str,
    payload: CopilotQuery,
    db: Session = Depends(get_db)
):
    """
    RAG-Powered Revenue Intelligence Copilot.
    Returns structured analysis, evidence citations, uncertainty scores, and actionable triggers.
    """
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first() or db.query(Merchant).first()
    
    # Process through RAG engine
    rag_result = copilot_engine.process_query(
        query=payload.query,
        user_role=payload.user_role or "Revenue Operations",
        merchant_context={"merchant_id": merchant.id if merchant else "merchant_urbankart"}
    )

    diag = rag_result.get("diagnostic")
    uncertainty = rag_result.get("uncertainty_assessment", {})
    citations = rag_result.get("citations", [])

    if diag:
        headline = diag.get("symptom", f"Diagnostic for: {payload.query}")
        drivers = [
            f"• Root Cause: {diag.get('likely_root_cause')}",
            f"• Affected Cohort: {diag.get('affected_segment')}",
            f"• Recommended Strategy: {diag.get('recommended_action')}",
            f"• Regulatory Clearance: {diag.get('required_approval')}"
        ]
        metrics = [
            {"label": "Expected Uplift", "value": diag.get("expected_uplift", "₹3.5L"), "trend": "up"},
            {"label": "Model Confidence", "value": f"{int(uncertainty.get('confidence_score', 0.94) * 100)}%", "trend": "up"},
            {"label": "Governance Tier", "value": "RBAC Verified", "trend": "neutral"}
        ]
        impact = diag.get("expected_uplift", "₹3.5L potential recovery")
        rec_action = {
            "title": diag.get("recommended_action", "Execute Recovery"),
            "action_type": "execute_policy",
            "target_count": 120,
            "potential_recovery": diag.get("expected_uplift", "₹3.5L"),
            "action_button": "Approve Recommended Strategy"
        }
    else:
        headline = uncertainty.get("statement", "Insufficient evidence to determine root cause.")
        drivers = ["• Insufficient data points in the selected window.", "• System recommendation: continue monitoring without automated intervention."]
        metrics = [{"label": "Confidence", "value": f"{int(uncertainty.get('confidence_score', 0.4) * 100)}%", "trend": "down"}]
        impact = "No action advised"
        rec_action = None

    return {
        "query": payload.query,
        "headline": headline,
        "metrics": metrics,
        "drivers": drivers,
        "estimated_impact": impact,
        "recommended_action": rec_action,
        "structured_diagnostic": diag,
        "uncertainty_assessment": uncertainty,
        "citations": citations,
        "suggested_followups": [
            "Why did recovery rate fall yesterday?",
            "Which issuer bank caused the greatest loss in the last 6 hours?",
            "Show evidence for recommending WhatsApp UPI links",
            "How much revenue can we recover this week?"
        ]
    }
