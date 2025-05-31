from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from db import SessionLocal
from models import Product, ProductImage
from auth import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/search", tags=["Search"])

class SearchProductItem(BaseModel):
    id: int
    name: str
    price_per_day: float
    original_price: float
    discount_percentage: int
    rating: float
    review_count: int
    image_url: str
    is_favorited: bool = False
    class Config:
        from_attributes = True

class SearchResponse(BaseModel):
    success: bool
    data: dict

class SuggestionResponse(BaseModel):
    success: bool
    data: dict

@router.get("", response_model=SearchResponse)
def search_products(
    q: str = Query(..., min_length=1),
    category_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Product).options(joinedload(Product.images))
    query = query.filter(Product.name.ilike(f"%{q}%"))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    total_results = query.count()
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()
    result = []
    for p in products:
        image_url = p.images[0].image_url if p.images else ""
        result.append(SearchProductItem(
            id=p.id,
            name=p.name,
            price_per_day=p.price_per_day,
            original_price=p.original_price,
            discount_percentage=p.discount_percentage,
            rating=p.rating,
            review_count=p.review_count,
            image_url=image_url,
            is_favorited=False
        ))
    return {"success": True, "data": {"query": q, "total_results": total_results, "products": result}}

@router.get("/suggestions", response_model=SuggestionResponse)
def search_suggestions(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    # Ambil 10 nama produk unik yang mengandung q
    suggestions = db.query(Product.name).filter(Product.name.ilike(f"%{q}%")).distinct().limit(10).all()
    suggestion_list = [s[0] for s in suggestions]
    return {"success": True, "data": {"suggestions": suggestion_list}} 