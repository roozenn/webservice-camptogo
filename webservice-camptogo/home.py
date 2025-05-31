from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel
from typing import List
from db import SessionLocal
from models import Banner, Category, Product

router = APIRouter(prefix="/home", tags=["Home/Beranda"])

# Response Models
class BannerItem(BaseModel):
    id: int
    title: str
    description: str
    image_url: str
    link_url: str
    class Config:
        from_attributes = True

class BannerResponse(BaseModel):
    success: bool
    data: List[BannerItem]

class CategoryItem(BaseModel):
    id: int
    name: str
    description: str
    icon_url: str
    class Config:
        from_attributes = True

class CategoryResponse(BaseModel):
    success: bool
    data: List[CategoryItem]

class ProductRecommendationItem(BaseModel):
    id: int
    name: str
    price_per_day: float
    original_price: float
    discount_percentage: int
    rating: float
    review_count: int
    image_url: str
    is_favorited: bool

class ProductRecommendationResponse(BaseModel):
    success: bool
    data: List[ProductRecommendationItem]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint: /home/banners
@router.get("/banners", response_model=BannerResponse)
def get_banners(db=Depends(get_db)):
    banners = db.query(Banner).all()
    return {"success": True, "data": [BannerItem.from_orm(b) for b in banners]}

# Endpoint: /home/categories
@router.get("/categories", response_model=CategoryResponse)
def get_categories(db=Depends(get_db)):
    categories = db.query(Category).all()
    return {"success": True, "data": [CategoryItem.from_orm(c) for c in categories]}

# Endpoint: /home/recommendations/beginner
@router.get("/recommendations/beginner", response_model=ProductRecommendationResponse)
def get_recommendations_beginner(limit: int = Query(10, ge=1, le=50), db=Depends(get_db)):
    products = db.query(Product).order_by(Product.price_per_day.asc()).limit(limit).all()
    return {"success": True, "data": [ProductRecommendationItem(
        id=p.id,
        name=p.name,
        price_per_day=p.price_per_day,
        original_price=p.original_price,
        discount_percentage=p.discount_percentage,
        rating=p.rating,
        review_count=p.review_count,
        image_url=p.images[0].image_url if p.images else "",
        is_favorited=False
    ) for p in products]}

# Endpoint: /home/recommendations/popular
@router.get("/recommendations/popular", response_model=ProductRecommendationResponse)
def get_recommendations_popular(limit: int = Query(10, ge=1, le=50), db=Depends(get_db)):
    products = db.query(Product).order_by(Product.rating.desc()).limit(limit).all()
    return {"success": True, "data": [ProductRecommendationItem(
        id=p.id,
        name=p.name,
        price_per_day=p.price_per_day,
        original_price=p.original_price,
        discount_percentage=p.discount_percentage,
        rating=p.rating,
        review_count=p.review_count,
        image_url=p.images[0].image_url if p.images else "",
        is_favorited=False
    ) for p in products]}

# Enable ORM mode for Pydantic models
BannerItem.Config = type('Config', (), {'orm_mode': True})
CategoryItem.Config = type('Config', (), {'orm_mode': True}) 