from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Merchant, AgentAction
import json

router = APIRouter()


@router.post("/merchants/{merchant_id}/agent/query")
async def agent_query(
    merchant_id: str,
    query: str,
    db: Session = Depends(get_db)
):
    """Submit a query to the RevPilot agent"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    # Placeholder: Agent orchestration will be added in Phase 4
    return {
        "query": query,
        "status": "processing",
        "message": "Agent orchestration coming in Phase 4"
    }


@router.post("/merchants/{merchant_id}/agent/approve-action")
async def approve_action(
    merchant_id: str,
    action_id: str,
    approved: bool,
    db: Session = Depends(get_db)
):
    """Approve or reject a sensitive agent action"""
    action = db.query(AgentAction).filter(
        AgentAction.merchant_id == merchant_id,
        AgentAction.id == action_id
    ).first()
    
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    # Placeholder: Approval flow will be implemented in Phase 4
    return {
        "action_id": action_id,
        "approved": approved,
        "status": "approval_recorded"
    }
