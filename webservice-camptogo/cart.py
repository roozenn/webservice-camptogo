from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, date
from models import Cart, Product, ProductImage, Coupon, User
from auth import get_db, get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/cart", tags=["Cart"])

# Response Models
class CartProductItem(BaseModel):
    id: int
    name: str
    image_url: str
    price_per_day: float
    deposit_amount: float
    class Config:
        from_attributes = True

class CartItem(BaseModel):
    id: int
    product: CartProductItem
    start_date: date
    end_date: date
    days_count: int
    quantity: int
    subtotal: float
    deposit_subtotal: float
    class Config:
        from_attributes = True

class CartSummary(BaseModel):
    total_rental: float
    total_deposit: float
    total_amount: float

class CartListResponse(BaseModel):
    success: bool
    data: dict

class SimpleResponse(BaseModel):
    success: bool
    message: str

class ValidateCouponRequest(BaseModel):
    coupon_code: str

class ValidateCouponResponseData(BaseModel):
    valid: bool
    discount_amount: float
    message: str

class ValidateCouponResponse(BaseModel):
    success: bool
    data: ValidateCouponResponseData

# Helper

def calculate_days(start_date: str, end_date: str) -> int:
    d1 = datetime.strptime(start_date, "%Y-%m-%d").date()
    d2 = datetime.strptime(end_date, "%Y-%m-%d").date()
    return (d2 - d1).days + 1

def get_cart_items(user: User, db: Session):
    items = db.query(Cart).filter(Cart.user_id == user.id).options(joinedload(Cart.product).joinedload(Product.images)).all()
    result = []
    total_rental = 0
    total_deposit = 0
    for item in items:
        product = item.product
        days_count = calculate_days(item.start_date, item.end_date)
        subtotal = product.price_per_day * days_count * item.quantity
        deposit_subtotal = product.deposit_amount * item.quantity
        total_rental += subtotal
        total_deposit += deposit_subtotal
        result.append(CartItem(
            id=item.id,
            product=CartProductItem(
                id=product.id,
                name=product.name,
                image_url=product.images[0].image_url if product.images else "",
                price_per_day=product.price_per_day,
                deposit_amount=product.deposit_amount
            ),
            start_date=item.start_date,
            end_date=item.end_date,
            days_count=days_count,
            quantity=item.quantity,
            subtotal=subtotal,
            deposit_subtotal=deposit_subtotal
        ))
    summary = CartSummary(
        total_rental=total_rental,
        total_deposit=total_deposit,
        total_amount=total_rental + total_deposit
    )
    return result, summary

# Endpoint: GET /cart
@router.get("", response_model=CartListResponse)
def get_cart(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items, summary = get_cart_items(user, db)
    return {"success": True, "data": {"items": items, "summary": summary}}

# Endpoint: POST /cart
class AddCartRequest(BaseModel):
    product_id: int
    start_date: date
    end_date: date
    quantity: int

@router.post("", response_model=SimpleResponse)
def add_to_cart(req: AddCartRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == req.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if req.quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity minimal 1")
    # Optional: validasi tanggal
    cart_item = Cart(
        user_id=user.id,
        product_id=product.id,
        start_date=str(req.start_date),
        end_date=str(req.end_date),
        quantity=req.quantity
    )
    db.add(cart_item)
    db.commit()
    return {"success": True, "message": "Item berhasil ditambahkan ke keranjang"}

# Endpoint: PUT /cart/{cart_id}
class UpdateCartRequest(BaseModel):
    start_date: date
    end_date: date
    quantity: int

@router.put("/{cart_id}", response_model=SimpleResponse)
def update_cart(cart_id: int, req: UpdateCartRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_item = db.query(Cart).filter(Cart.id == cart_id, Cart.user_id == user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    cart_item.start_date = str(req.start_date)
    cart_item.end_date = str(req.end_date)
    cart_item.quantity = req.quantity
    db.commit()
    return {"success": True, "message": "Item keranjang berhasil diupdate"}

# Endpoint: DELETE /cart/{cart_id}
@router.delete("/{cart_id}", response_model=SimpleResponse)
def delete_cart(cart_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_item = db.query(Cart).filter(Cart.id == cart_id, Cart.user_id == user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(cart_item)
    db.commit()
    return {"success": True, "message": "Item keranjang berhasil dihapus"}

# Endpoint: POST /cart/validate-coupon
@router.post("/validate-coupon", response_model=ValidateCouponResponse)
def validate_coupon(req: ValidateCouponRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    coupon = db.query(Coupon).filter(Coupon.code == req.coupon_code, Coupon.is_active == True).first()
    if not coupon:
        return {"success": True, "data": {"valid": False, "discount_amount": 0, "message": "Kupon tidak ditemukan atau tidak aktif"}}
    if coupon.valid_until and coupon.valid_until < datetime.utcnow():
        return {"success": True, "data": {"valid": False, "discount_amount": 0, "message": "Kupon sudah kadaluarsa"}}
    return {"success": True, "data": {"valid": True, "discount_amount": coupon.discount_amount, "message": "Kupon valid"}} 