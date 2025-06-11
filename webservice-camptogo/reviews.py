from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from models import ProductReview, Product, Order, OrderItem, User
from auth import get_db, get_current_user
from pydantic import BaseModel
import json, os, shutil
from sqlalchemy import func

router = APIRouter(prefix="/reviews", tags=["Reviews"])

UPLOAD_REVIEW_DIR = "./uploads/review_images"
if not os.path.exists(UPLOAD_REVIEW_DIR):
    os.makedirs(UPLOAD_REVIEW_DIR)

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

# Endpoint: POST /reviews
@router.post("", response_model=SimpleResponse)
async def add_review(
    product_id: int = Form(...),
    order_id: int = Form(...),
    rating: int = Form(..., ge=1, le=5),
    comment: Optional[str] = Form(""),
    files: Optional[List[UploadFile]] = File(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate Order and Product belong to user and order
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order tidak ditemukan atau bukan milik user")

    order_item = db.query(OrderItem).filter(OrderItem.order_id == order_id, OrderItem.product_id == product_id).first()
    if not order_item:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Produk ini tidak ada dalam pesanan ini")

    # Check if review already exists for this order item
    existing_review = db.query(ProductReview).filter(ProductReview.order_id == order_id, ProductReview.product_id == product_id, ProductReview.user_id == user.id).first()
    if existing_review:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Anda sudah memberikan ulasan untuk produk ini pada pesanan ini")

    # Handle file upload
    image_urls = []
    if files:
        for file in files:
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in [".jpg", ".jpeg", ".png"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Format file tidak diizinkan. Gunakan JPG, JPEG, atau PNG.")
            filename = f"{user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{file.filename}"
            file_path = os.path.join(UPLOAD_REVIEW_DIR, filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            image_urls.append(f"/uploads/review_images/{filename}")

    # Create new review
    new_review = ProductReview(
        product_id=product_id,
        user_id=user.id,
        order_id=order_id,
        user_name=user.full_name,
        user_profile_picture=user.profile_picture,
        rating=rating,
        comment=comment,
        images=json.dumps(image_urls),
        created_at=datetime.utcnow()
    )

    db.add(new_review)
    db.commit()

    # Update product average rating and review count
    update_product_rating(product_id, db)

    return {"success": True, "message": "Ulasan berhasil ditambahkan"} 