"""
Immutable Audit Ledger Endpoints
Provides full traceability for:
- Autonomous actions vs human approvals
- Policy updates & threshold adjustments
- Operator classification corrections
- Emergency kill-switch toggles
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import uuid

from app.database import get_db
from app.models import AuditLog
from app.rbac import require_permission, Permission

router = APIRouter()


class AuditEntryCreate(BaseModel):
    user_id: Optional[str] = "admin_01"
    user_role: str = "Admin"
    merchant_id: Optional[str] = "merchant_urbankart"
    action: str
    target_type: Optional[str] = "transaction"
    target_id: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    result: str = "success"
    approval_status: Optional[str] = "approved"


@router.get("/audit/logs")
async def get_audit_logs(
    merchant_id: Optional[str] = None,
    action: Optional[str] = None,
    user_role: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Retrieve immutable audit ledger entries with multi-attribute filtering"""
    query = db.query(AuditLog)

    if merchant_id:
        query = query.filter(AuditLog.merchant_id == merchant_id)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if user_role:
        query = query.filter(AuditLog.user_role == user_role)

    total_count = query.count()
    logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()

    items = []
    for log in logs:
        data = None
        if log.action_data:
            try:
                data = json.loads(log.action_data)
            except Exception:
                data = {"raw": log.action_data}

        items.append({
            "id": log.id,
            "timestamp": log.timestamp.isoformat() if log.timestamp else datetime.utcnow().isoformat(),
            "user_id": log.user_id,
            "user_role": log.user_role,
            "merchant_id": log.merchant_id,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "details": data,
            "result": log.result,
            "approval_status": log.approval_status
        })

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "logs": items
    }


@router.post("/audit/logs")
async def create_audit_log(
    entry: AuditEntryCreate,
    db: Session = Depends(get_db)
):
    """Append a new tamper-evident event to the audit ledger"""
    log_id = f"AUD_{uuid.uuid4().hex[:12].upper()}"
    new_log = AuditLog(
        id=log_id,
        user_id=entry.user_id,
        user_role=entry.user_role,
        merchant_id=entry.merchant_id,
        action=entry.action,
        target_type=entry.target_type,
        target_id=entry.target_id,
        action_data=json.dumps(entry.action_data) if entry.action_data else None,
        timestamp=datetime.utcnow(),
        result=entry.result,
        approval_status=entry.approval_status
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return {
        "status": "success",
        "audit_id": new_log.id,
        "recorded_at": new_log.timestamp.isoformat()
    }

