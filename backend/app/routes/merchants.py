from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Merchant
import uuid

router = APIRouter()


@router.post("/merchants")
async def create_merchant(name: str, db: Session = Depends(get_db)):
    """Create a new merchant"""
    merchant_id = str(uuid.uuid4())
    merchant = Merchant(id=merchant_id, name=name, api_key=str(uuid.uuid4()))
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    return {"id": merchant.id, "name": merchant.name, "api_key": merchant.api_key}


@router.get("/merchants/{merchant_id}")
async def get_merchant(merchant_id: str, db: Session = Depends(get_db)):
    """Get merchant details"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return {"id": merchant.id, "name": merchant.name, "created_at": merchant.created_at}
