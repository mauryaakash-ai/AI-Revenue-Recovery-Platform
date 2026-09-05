"""
Multi-Armed Bandit Routing & Governance Endpoints
Endpoints:
- GET  /api/v1/bandit/arms
- POST /api/v1/bandit/feedback
- POST /api/v1/bandit/kill-switch
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.database import get_db
from app.bandit_engine import bandit_engine

router = APIRouter()


class FeedbackRequest(BaseModel):
    arm_name: str
    recovered: bool
    net_revenue: float = 0.0


class KillSwitchRequest(BaseModel):
    arm_name: str
    active: bool


@router.get("/bandit/arms")
async def get_bandit_arms():
    """Retrieve current status, pulls, rewards, and conversion rates of all bandit arms"""
    return {
        "arms": bandit_engine.get_arms_status(),
        "total_bandit_pulls": bandit_engine.total_pulls,
        "algorithm": "UCB1 (Upper Confidence Bound) with Exploration C=1.414"
    }


@router.post("/bandit/feedback")
async def post_bandit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    """Record recovery outcome to update arm empirical rewards and posterior distributions"""
    if request.arm_name not in bandit_engine.arms:
        raise HTTPException(status_code=404, detail=f"Bandit arm '{request.arm_name}' not found")

    bandit_engine.record_feedback(
        arm_name=request.arm_name,
        recovered=request.recovered,
        net_revenue=request.net_revenue,
        db=db
    )
    return {
        "status": "success",
        "message": f"Updated feedback for arm {request.arm_name}",
        "current_conversion_rate": bandit_engine.arms[request.arm_name].conversion_rate
    }


@router.post("/bandit/kill-switch")
async def toggle_bandit_kill_switch(request: KillSwitchRequest):
    """Safely toggle the emergency kill switch for any experimentation arm"""
    success = bandit_engine.set_kill_switch(request.arm_name, request.active)
    if not success:
        raise HTTPException(status_code=404, detail=f"Bandit arm '{request.arm_name}' not found")

    status_str = "ENABLED" if request.active else "KILLED/DISABLED"
    return {
        "status": "success",
        "arm_name": request.arm_name,
        "is_active": request.active,
        "message": f"Arm {request.arm_name} is now {status_str}"
    }

