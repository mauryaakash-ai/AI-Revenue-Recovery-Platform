"""
Real-time operational & anomaly alerts routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models import Merchant, Alert, AuditLog

router = APIRouter()


class AlertActionPayload(BaseModel):
    action: str  # acknowledge, snooze, resolve, dismiss


@router.get("/merchants/{merchant_id}/alerts")
async def get_alerts(
    merchant_id: str,
    db: Session = Depends(get_db)
):
    """Get real-time operational and anomaly alerts"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first() or db.query(Merchant).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    alerts = db.query(Alert).filter(
        Alert.merchant_id == merchant.id
    ).order_by(Alert.detected_at.desc()).all()

    items = []
    for a in alerts:
        items.append({
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "detected_at": a.detected_at.isoformat(),
            "potential_impact": a.potential_impact,
            "ai_assessment": a.ai_assessment,
            "status": a.status,
            "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None
        })

    return {
        "active_count": sum(1 for a in alerts if a.status == "active"),
        "alerts": items
    }


@router.post("/merchants/{merchant_id}/alerts/{alert_id}/action")
async def handle_alert_action(
    merchant_id: str,
    alert_id: str,
    payload: AlertActionPayload,
    db: Session = Depends(get_db)
):
    """Acknowledge, snooze, or resolve an alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if payload.action == "resolve":
        alert.status = "resolved"
        alert.resolved_at = datetime.utcnow()
    elif payload.action == "snooze":
        alert.status = "snoozed"
    elif payload.action == "acknowledge":
        alert.status = "acknowledged"

    db.commit()

    return {
        "status": "success",
        "alert_id": alert.id,
        "new_status": alert.status,
        "message": f"Alert marked as {alert.status}."
    }

