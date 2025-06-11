from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import PaymentMethod, User
from auth import get_db, get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/payment-methods", tags=["Payment Methods"])

class PaymentMethodItem(BaseModel):
    id: int
    method_type: str
    provider_name: str
    account_number: str
    account_name: str
    is_default: bool
    class Config:
        from_attributes = True

class PaymentMethodListResponse(BaseModel):
    success: bool
    data: List[PaymentMethodItem]

class SimpleResponse(BaseModel):
    success: bool
    message: str

class AddPaymentMethodRequest(BaseModel):
    method_type: str
    provider_name: str
    account_number: str
    account_name: str
    is_default: bool = False

@router.get("", response_model=PaymentMethodListResponse)
def get_payment_methods(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    methods = db.query(PaymentMethod).filter(PaymentMethod.user_id == user.id).all()
    return {"success": True, "data": methods}

@router.post("", response_model=SimpleResponse)
def add_payment_method(req: AddPaymentMethodRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.is_default:
        db.query(PaymentMethod).filter(PaymentMethod.user_id == user.id).update({PaymentMethod.is_default: False})
    method = PaymentMethod(
        user_id=user.id,
        method_type=req.method_type,
        provider_name=req.provider_name,
        account_number=req.account_number,
        account_name=req.account_name,
        is_default=req.is_default
    )
    db.add(method)
    db.commit()
    return {"success": True, "message": "Metode pembayaran berhasil ditambahkan"} 