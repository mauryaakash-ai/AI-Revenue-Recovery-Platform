"""
Merchant Recovery Policy Configuration & Failure Correction Endpoints
Endpoints:
- GET  /api/v1/merchants/{merchant_id}/policies
- PUT  /api/v1/merchants/{merchant_id}/policies
- POST /api/v1/failures/{failure_id}/correct
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from app.database import get_db
from app.models import MerchantPolicy, FailureClassificationCorrection, Merchant
from app.rbac import require_permission, Permission

router = APIRouter()


class PolicyUpdateRequest(BaseModel):
    auto_approval_threshold: Optional[float] = 0.80
    max_autonomous_amount: Optional[float] = 10000.0
    max_retries_per_txn: Optional[int] = 3
    quiet_hours_enabled: Optional[bool] = True
    quiet_hours_start_ist: Optional[int] = 21
    quiet_hours_end_ist: Optional[int] = 8
    min_roi_requirement: Optional[float] = 150.0
    allowed_channels: Optional[List[str]] = ["whatsapp_upi_intent", "sms_payment_link", "delayed_card_retry"]


class FailureCorrectionRequest(BaseModel):
    transaction_id: str
    original_category: str
    corrected_category: str
    corrected_subcategory: str
    correction_notes: Optional[str] = "Operator override based on customer support ticket verification"


@router.get("/merchants/{merchant_id}/policies")
async def get_merchant_policies(merchant_id: str, db: Session = Depends(get_db)):
    """Retrieve active recovery and governance policy for a merchant"""
    policy = db.query(MerchantPolicy).filter(MerchantPolicy.merchant_id == merchant_id).first()
    if not policy:
        # Fallback to first policy or return enterprise defaults
        policy = db.query(MerchantPolicy).first()

    if not policy:
        return {
            "merchant_id": merchant_id,
            "policy_name": "Standard Enterprise Recovery Policy",
            "auto_approval_threshold": 0.80,
            "max_autonomous_amount": 10000.0,
            "max_retries_per_txn": 3,
            "quiet_hours_enabled": True,
            "quiet_hours_start_ist": 21,
            "quiet_hours_end_ist": 8,
            "min_roi_requirement": 150.0,
            "allowed_channels": ["whatsapp_upi_intent", "sms_payment_link", "delayed_card_retry", "dynamic_vpa"],
            "risk_score_threshold": 50.0,
            "is_active": True
        }

    channels = []
    if policy.allowed_channels:
        try:
            channels = json.loads(policy.allowed_channels)
        except Exception:
            channels = [policy.allowed_channels]

    return {
        "id": policy.id,
        "merchant_id": policy.merchant_id,
        "policy_name": policy.policy_name,
        "auto_approval_threshold": policy.auto_approval_threshold,
        "max_autonomous_amount": policy.max_autonomous_amount,
        "max_retries_per_txn": policy.max_retries_per_txn,
        "quiet_hours_enabled": policy.quiet_hours_enabled,
        "quiet_hours_start_ist": policy.quiet_hours_start_ist,
        "quiet_hours_end_ist": policy.quiet_hours_end_ist,
        "min_roi_requirement": policy.min_roi_requirement,
        "allowed_channels": channels,
        "risk_score_threshold": policy.risk_score_threshold,
        "is_active": policy.is_active,
        "updated_at": policy.updated_at.isoformat() if policy.updated_at else datetime.utcnow().isoformat()
    }


@router.put("/merchants/{merchant_id}/policies")
async def update_merchant_policies(
    merchant_id: str,
    req: PolicyUpdateRequest,
    db: Session = Depends(get_db),
    actor_role: str = Depends(require_permission(Permission.CONFIGURE))
):
    """Update merchant recovery thresholds and governance rules with audit trail"""
    policy = db.query(MerchantPolicy).filter(MerchantPolicy.merchant_id == merchant_id).first()
    if not policy:
        policy = MerchantPolicy(
            merchant_id=merchant_id,
            policy_name=f"{merchant_id.capitalize()} Recovery Policy"
        )
        db.add(policy)

    if req.auto_approval_threshold is not None:
        policy.auto_approval_threshold = req.auto_approval_threshold
    if req.max_autonomous_amount is not None:
        policy.max_autonomous_amount = req.max_autonomous_amount
    if req.max_retries_per_txn is not None:
        policy.max_retries_per_txn = req.max_retries_per_txn
    if req.quiet_hours_enabled is not None:
        policy.quiet_hours_enabled = req.quiet_hours_enabled
    if req.quiet_hours_start_ist is not None:
        policy.quiet_hours_start_ist = req.quiet_hours_start_ist
    if req.quiet_hours_end_ist is not None:
        policy.quiet_hours_end_ist = req.quiet_hours_end_ist
    if req.min_roi_requirement is not None:
        policy.min_roi_requirement = req.min_roi_requirement
    if req.allowed_channels is not None:
        policy.allowed_channels = json.dumps(req.allowed_channels)

    policy.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(policy)

    return {
        "status": "success",
        "message": "Merchant policy updated successfully",
        "policy_id": policy.id,
        "updated_by_role": actor_role
    }


@router.post("/failures/{failure_id}/correct")
async def correct_failure_classification(
    failure_id: str,
    req: FailureCorrectionRequest,
    db: Session = Depends(get_db),
    actor_role: str = Depends(require_permission(Permission.UPDATE))
):
    """Operator human-in-the-loop correction of AI failure classification"""
    correction = FailureClassificationCorrection(
        transaction_id=req.transaction_id,
        original_category=req.original_category,
        corrected_category=req.corrected_category,
        corrected_subcategory=req.corrected_subcategory,
        correction_notes=req.correction_notes,
        reviewed_by=f"Operator ({actor_role})",
        confidence_score=0.99
    )
    db.add(correction)
    db.commit()
    db.refresh(correction)

    return {
        "status": "success",
        "message": "Failure classification corrected and stored for active model retraining feedback",
        "correction_id": correction.id,
        "transaction_id": req.transaction_id,
        "new_category": req.corrected_category,
        "new_subcategory": req.corrected_subcategory
    }

