from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime
from db import SessionLocal
from models import Favorite, Product, ProductImage, User
from auth import get_db, security, SECRET_KEY, ALGORITHM, get_current_user
from jose import jwt, JWTError
from pydantic import BaseModel

router = APIRouter(prefix="/favorites", tags=["Favorites"])

# Response Model
class FavoriteProductItem(BaseModel):
    id: int
    name: str
    price_per_day: float
    original_price: float
    discount_percentage: int
    rating: float
    review_count: int
    image_url: str
    added_at: datetime

    class Config:
        from_attributes = True

class FavoritesResponse(BaseModel):
    success: bool
    data: List[FavoriteProductItem]

class SimpleResponse(BaseModel):
    success: bool
    message: str

@router.get("", response_model=FavoritesResponse)
def get_favorites(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    print("GET_FAVORITES CALLED")
    favorites = db.query(Favorite).filter(Favorite.user_id == user.id).join(Product).options(joinedload(Favorite.product).joinedload(Product.images)).all()
    result = []
    for fav in favorites:
        product = fav.product
        image_url = product.images[0].image_url if product.images else ""
        result.append(FavoriteProductItem(
            id=product.id,
            name=product.name,
            price_per_day=product.price_per_day,
            original_price=product.original_price,
            discount_percentage=product.discount_percentage,
            rating=product.rating,
            review_count=product.review_count,
            image_url=image_url,
            added_at=fav.added_at
        ))
    return {"success": True, "data": result}

@router.post("/{product_id}", response_model=SimpleResponse)
def add_favorite(product_id: int = Path(..., ge=1), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    existing = db.query(Favorite).filter(Favorite.user_id == user.id, Favorite.product_id == product_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product already in favorites")
    fav = Favorite(user_id=user.id, product_id=product_id)
    db.add(fav)
    db.commit()
    return {"success": True, "message": "Product added to favorites"}

@router.delete("/{product_id}", response_model=SimpleResponse)
def remove_favorite(product_id: int = Path(..., ge=1), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    fav = db.query(Favorite).filter(Favorite.user_id == user.id, Favorite.product_id == product_id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(fav)
    db.commit()
    return {"success": True, "message": "Product removed from favorites"} 