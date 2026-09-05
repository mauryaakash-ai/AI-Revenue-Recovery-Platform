"""
Bank & Gateway Real-Time Health Monitoring Endpoints
Tracks:
- Success rates, failure spikes, timeout rates, and latency
- Anomaly detection scoring
- Automated retry throttling and smart rerouting recommendations
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.database import get_db
from app.models import BankHealthRecord, GatewayHealthRecord

router = APIRouter()

# In-memory baseline status for realistic simulation and local development
BANK_STATUS_STORE: Dict[str, Dict[str, Any]] = {
    "HDFC Bank": {
        "bank_code": "HDFC",
        "bank_name": "HDFC Bank",
        "success_rate": 0.942,
        "failure_rate": 0.041,
        "timeout_rate": 0.017,
        "avg_latency_ms": 320.0,
        "anomaly_score": 4.5,
        "incident_status": "HEALTHY",
        "recommended_action": "NORMAL",
        "last_updated": datetime.utcnow().isoformat()
    },
    "State Bank of India": {
        "bank_code": "SBI",
        "bank_name": "State Bank of India",
        "success_rate": 0.812,
        "failure_rate": 0.148,
        "timeout_rate": 0.040,
        "avg_latency_ms": 1150.0,
        "anomaly_score": 68.2,
        "incident_status": "DEGRADED",
        "recommended_action": "THROTTLE_RETRIES",
        "last_updated": datetime.utcnow().isoformat()
    },
    "ICICI Bank": {
        "bank_code": "ICICI",
        "bank_name": "ICICI Bank",
        "success_rate": 0.958,
        "failure_rate": 0.032,
        "timeout_rate": 0.010,
        "avg_latency_ms": 280.0,
        "anomaly_score": 2.1,
        "incident_status": "HEALTHY",
        "recommended_action": "NORMAL",
        "last_updated": datetime.utcnow().isoformat()
    },
    "Axis Bank": {
        "bank_code": "AXIS",
        "bank_name": "Axis Bank",
        "success_rate": 0.925,
        "failure_rate": 0.055,
        "timeout_rate": 0.020,
        "avg_latency_ms": 410.0,
        "anomaly_score": 11.4,
        "incident_status": "HEALTHY",
        "recommended_action": "NORMAL",
        "last_updated": datetime.utcnow().isoformat()
    },
    "Kotak Mahindra Bank": {
        "bank_code": "KOTAK",
        "bank_name": "Kotak Mahindra Bank",
        "success_rate": 0.938,
        "failure_rate": 0.045,
        "timeout_rate": 0.017,
        "avg_latency_ms": 360.0,
        "anomaly_score": 6.8,
        "incident_status": "HEALTHY",
        "recommended_action": "NORMAL",
        "last_updated": datetime.utcnow().isoformat()
    }
}

GATEWAY_STATUS_STORE: Dict[str, Dict[str, Any]] = {
    "razorpay": {
        "gateway_name": "Razorpay",
        "gateway_id": "razorpay",
        "success_rate": 0.962,
        "failure_rate": 0.028,
        "timeout_rate": 0.010,
        "avg_latency_ms": 180.0,
        "anomaly_score": 3.0,
        "incident_status": "HEALTHY",
        "recommended_action": "NORMAL",
        "last_updated": datetime.utcnow().isoformat()
    },
    "payu": {
        "gateway_name": "PayU",
        "gateway_id": "payu",
        "success_rate": 0.934,
        "failure_rate": 0.048,
        "timeout_rate": 0.018,
        "avg_latency_ms": 290.0,
        "anomaly_score": 12.0,
        "incident_status": "HEALTHY",
        "recommended_action": "NORMAL",
        "last_updated": datetime.utcnow().isoformat()
    },
    "stripe": {
        "gateway_name": "Stripe",
        "gateway_id": "stripe",
        "success_rate": 0.978,
        "failure_rate": 0.018,
        "timeout_rate": 0.004,
        "avg_latency_ms": 140.0,
        "anomaly_score": 1.5,
        "incident_status": "HEALTHY",
        "recommended_action": "NORMAL",
        "last_updated": datetime.utcnow().isoformat()
    },
    "billdesk": {
        "gateway_name": "BillDesk",
        "gateway_id": "billdesk",
        "success_rate": 0.908,
        "failure_rate": 0.062,
        "timeout_rate": 0.030,
        "avg_latency_ms": 520.0,
        "anomaly_score": 24.5,
        "incident_status": "DEGRADED",
        "recommended_action": "REROUTE_CHANNEL",
        "last_updated": datetime.utcnow().isoformat()
    }
}


class BankSimulationRequest(BaseModel):
    bank_name: str
    failure_rate_spike: float = 0.25
    avg_latency_ms: float = 1450.0
    status: Optional[str] = "DEGRADED"


@router.get("/banks/health")
async def get_banks_health(db: Session = Depends(get_db)):
    """Retrieve real-time telemetry, latency, and degradation scores for issuer banks"""
    # Check DB records first
    db_records = db.query(BankHealthRecord).order_by(BankHealthRecord.id.desc()).limit(10).all()
    if db_records:
        latest_map = {}
        for rec in db_records:
            if rec.bank_name not in latest_map:
                latest_map[rec.bank_name] = {
                    "bank_name": rec.bank_name,
                    "success_rate": rec.success_rate,
                    "failure_rate": rec.failure_rate,
                    "timeout_rate": rec.timeout_rate,
                    "avg_latency_ms": rec.avg_latency_ms,
                    "anomaly_score": rec.anomaly_score,
                    "incident_status": rec.incident_status,
                    "recommended_action": rec.recommended_action,
                    "last_updated": rec.recorded_at.isoformat() if rec.recorded_at else datetime.utcnow().isoformat()
                }
        if len(latest_map) >= 3:
            return {"banks": list(latest_map.values())}

    return {"banks": list(BANK_STATUS_STORE.values())}


@router.get("/gateways/health")
async def get_gateways_health(db: Session = Depends(get_db)):
    """Retrieve health statistics, latency, and routing recommendations for payment gateways"""
    db_records = db.query(GatewayHealthRecord).order_by(GatewayHealthRecord.id.desc()).limit(10).all()
    if db_records:
        latest_map = {}
        for rec in db_records:
            if rec.gateway_name not in latest_map:
                latest_map[rec.gateway_name] = {
                    "gateway_name": rec.gateway_name,
                    "gateway_id": rec.gateway_name.lower(),
                    "success_rate": rec.success_rate,
                    "failure_rate": rec.failure_rate,
                    "timeout_rate": rec.timeout_rate,
                    "avg_latency_ms": rec.avg_latency_ms,
                    "anomaly_score": rec.anomaly_score,
                    "incident_status": rec.incident_status,
                    "recommended_action": rec.recommended_action,
                    "last_updated": rec.recorded_at.isoformat() if rec.recorded_at else datetime.utcnow().isoformat()
                }
        if len(latest_map) >= 3:
            return {"gateways": list(latest_map.values())}

    return {"gateways": list(GATEWAY_STATUS_STORE.values())}


@router.post("/banks/health/simulate")
async def simulate_bank_incident(req: BankSimulationRequest, db: Session = Depends(get_db)):
    """Interactive demo endpoint to simulate bank degradation and trigger RevPilot throttling"""
    bank_match = None
    for name, data in BANK_STATUS_STORE.items():
        if req.bank_name.lower() in name.lower():
            bank_match = name
            break

    if not bank_match:
        bank_match = req.bank_name
        BANK_STATUS_STORE[bank_match] = {
            "bank_code": bank_match[:4].upper(),
            "bank_name": bank_match,
            "success_rate": 0.90,
            "failure_rate": 0.08,
            "timeout_rate": 0.02,
            "avg_latency_ms": 300.0,
            "anomaly_score": 10.0,
            "incident_status": "HEALTHY",
            "recommended_action": "NORMAL"
        }

    item = BANK_STATUS_STORE[bank_match]
    item["failure_rate"] = round(req.failure_rate_spike, 3)
    item["success_rate"] = round(1.0 - req.failure_rate_spike, 3)
    item["avg_latency_ms"] = req.avg_latency_ms
    item["incident_status"] = req.status or ("DEGRADED" if req.failure_rate_spike > 0.15 else "HEALTHY")
    item["anomaly_score"] = round(min(100.0, req.failure_rate_spike * 350.0), 1)
    item["recommended_action"] = "THROTTLE_RETRIES" if item["incident_status"] == "DEGRADED" else "NORMAL"
    item["last_updated"] = datetime.utcnow().isoformat()

    # Persist in DB
    try:
        record = BankHealthRecord(
            bank_name=bank_match,
            success_rate=item["success_rate"],
            failure_rate=item["failure_rate"],
            timeout_rate=item["timeout_rate"],
            avg_latency_ms=item["avg_latency_ms"],
            anomaly_score=item["anomaly_score"],
            incident_status=item["incident_status"],
            recommended_action=item["recommended_action"]
        )
        db.add(record)
        db.commit()
    except Exception:
        db.rollback()

    return {
        "status": "success",
        "simulated_bank": bank_match,
        "details": item,
        "advisory": f"RevPilot policy engine will automatically throttle direct card retries for {bank_match} and reroute to alternate payment instruments."
    }

