from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List
from models import Address, User
from auth import get_db, get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/addresses", tags=["Addresses"])

# Response Models
class AddressItem(BaseModel):
    id: int
    recipient_name: str
    full_address: str
    phone_number: str
    is_default: bool
    class Config:
        from_attributes = True

class AddressListResponse(BaseModel):
    success: bool
    data: List[AddressItem]

class SimpleResponse(BaseModel):
    success: bool
    message: str
    data: dict = None

class AddAddressRequest(BaseModel):
    recipient_name: str
    full_address: str
    phone_number: str
    is_default: bool = False

class UpdateAddressRequest(BaseModel):
    recipient_name: str
    full_address: str
    phone_number: str
    is_default: bool = False

# Endpoint: GET /addresses
@router.get("", response_model=AddressListResponse)
def get_addresses(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    addresses = db.query(Address).filter(Address.user_id == user.id).all()
    return {"success": True, "data": addresses}

# Endpoint: POST /addresses
@router.post("", response_model=SimpleResponse)
def add_address(req: AddAddressRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.is_default:
        # Set semua alamat user lain jadi tidak default
        db.query(Address).filter(Address.user_id == user.id).update({Address.is_default: False})
    address = Address(
        user_id=user.id,
        recipient_name=req.recipient_name,
        full_address=req.full_address,
        phone_number=req.phone_number,
        is_default=req.is_default
    )
    db.add(address)
    db.commit()
    db.refresh(address)
    return {"success": True, "message": "Alamat berhasil ditambahkan", "data": {"id": address.id}}

# Endpoint: PUT /addresses/{address_id}
@router.put("/{address_id}", response_model=SimpleResponse)
def update_address(address_id: int, req: UpdateAddressRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    address = db.query(Address).filter(Address.id == address_id, Address.user_id == user.id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Alamat tidak ditemukan")
    if req.is_default:
        db.query(Address).filter(Address.user_id == user.id).update({Address.is_default: False})
    address.recipient_name = req.recipient_name
    address.full_address = req.full_address
    address.phone_number = req.phone_number
    address.is_default = req.is_default
    db.commit()
    return {"success": True, "message": "Alamat berhasil diupdate"}

# Endpoint: DELETE /addresses/{address_id}
@router.delete("/{address_id}", response_model=SimpleResponse)
def delete_address(address_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    address = db.query(Address).filter(Address.id == address_id, Address.user_id == user.id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Alamat tidak ditemukan")
    db.delete(address)
    db.commit()
    return {"success": True, "message": "Alamat berhasil dihapus"} 