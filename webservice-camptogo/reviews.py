from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from models import ProductReview, Product, Order, OrderItem, User
from auth import get_db, get_current_user
from pydantic import BaseModel, Field
import json
from sqlalchemy import func

router = APIRouter(prefix="/reviews", tags=["Reviews"])

# Request Body Model
class AddReviewRequest(BaseModel):
    product_id: int
    order_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = ""
    images: List[str] = []

# Response Model
class SimpleResponse(BaseModel):
    success: bool
    message: str

# Helper to update product rating/count
def update_product_rating(product_id: int, db: Session):
    avg_rating = db.query(func.avg(ProductReview.rating)).filter(ProductReview.product_id == product_id).scalar()
    review_count = db.query(ProductReview).filter(ProductReview.product_id == product_id).count()
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        product.rating = round(avg_rating, 1) if avg_rating is not None else 0.0
        product.review_count = review_count
        db.commit()
        # db.refresh(product) # Not needed here

# Endpoint: POST /reviews
@router.post("", response_model=SimpleResponse)
def add_review(req: AddReviewRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Validate Order and Product belong to user and order
    order = db.query(Order).filter(Order.id == req.order_id, Order.user_id == user.id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order tidak ditemukan atau bukan milik user")

    order_item = db.query(OrderItem).filter(OrderItem.order_id == req.order_id, OrderItem.product_id == req.product_id).first()
    if not order_item:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Produk ini tidak ada dalam pesanan ini")

    # Check if review already exists for this order item
    existing_review = db.query(ProductReview).filter(ProductReview.order_id == req.order_id, ProductReview.product_id == req.product_id, ProductReview.user_id == user.id).first()
    if existing_review:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Anda sudah memberikan ulasan untuk produk ini pada pesanan ini")

    # Create new review
    new_review = ProductReview(
        product_id=req.product_id,
        user_id=user.id,
        order_id=req.order_id,
        user_name=user.full_name, # Ambil dari user login
        user_profile_picture=user.profile_picture, # Ambil dari user login
        rating=req.rating,
        comment=req.comment,
        images=json.dumps(req.images), # Simpan list sebagai JSON string
        created_at=datetime.utcnow()
    )

    db.add(new_review)
    db.commit()
    # db.refresh(new_review) # Not needed here

    # Update product average rating and review count
    update_product_rating(req.product_id, db)

    return {"success": True, "message": "Ulasan berhasil ditambahkan"} 