from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Merchant
from app.agent import RevPilotAgent
import json

router = APIRouter()


@router.post("/merchants/{merchant_id}/agent/query")
async def agent_query(
    merchant_id: str,
    query: str,
    db: Session = Depends(get_db)
):
    """Submit a query to the RevPilot agent with SSE streaming"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    # Create agent and stream investigation
    agent = RevPilotAgent(db, merchant_id, provider_name="mock")
    
    async def stream_investigation():
        async for step in agent.investigate(query):
            yield f"data: {step}\n\n"
    
    return StreamingResponse(stream_investigation(), media_type="text/event-stream")


@router.post("/merchants/{merchant_id}/agent/approve-action")
async def approve_action(
    merchant_id: str,
    action_id: str,
    approved: bool,
    db: Session = Depends(get_db)
):
    """Approve or reject a sensitive agent action"""
    from app.models import AgentAction, ActionStatus
    
    action = db.query(AgentAction).filter(
        AgentAction.merchant_id == merchant_id,
        AgentAction.id == action_id
    ).first()
    
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    if approved:
        action.status = ActionStatus.APPROVED
        action.approval = "user_approved"
    else:
        action.status = ActionStatus.REJECTED
        action.approval = "user_rejected"
    
    db.commit()
    
    return {
        "action_id": action_id,
        "approved": approved,
        "status": action.status.value,
        "timestamp": action.created_at.isoformat()
    }

