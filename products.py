from fastapi import APIRouter, Query, Path, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc, func
import json

from db import SessionLocal
from models import Product, Category, ProductImage, ProductReview, Favorite, User
from auth import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])

# Response Models (pastikan from_attributes=True ditambahkan jika mapping langsung dari ORM)
class ProductItem(BaseModel):
    id: int
    name: str
    price_per_day: float
    original_price: float
    discount_percentage: int
    rating: float
    review_count: int
    image_url: str
    is_favorited: bool # Data dummy untuk sekarang, butuh relasi user di masa depan

    class Config:
        from_attributes = True

class Pagination(BaseModel):
    current_page: int
    total_pages: int
    total_items: int
    has_next: bool
    has_prev: bool

class ProductListData(BaseModel):
    products: List[ProductItem]
    pagination: Pagination

class ProductListResponse(BaseModel):
    success: bool
    data: ProductListData

class CategoryShort(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class ProductImageItem(BaseModel): # Rename to avoid conflict with ORM model
    id: int
    image_url: str
    is_primary: bool

    class Config:
        from_attributes = True

class ProductDetailData(BaseModel):
    id: int
    name: str
    description: str
    price_per_day: float
    original_price: float
    discount_percentage: int
    deposit_amount: float
    rating: float
    review_count: int
    stock_quantity: int
    category: CategoryShort
    images: List[ProductImageItem]
    is_favorited: bool # Data dummy untuk sekarang

class ProductDetailResponse(BaseModel):
    success: bool
    data: ProductDetailData

class ReviewUser(BaseModel):
    name: str
    profile_picture: str

class ReviewItem(BaseModel):
    id: int
    user: ReviewUser
    rating: int
    comment: str
    images: List[str]
    created_at: datetime

    class Config:
        from_attributes = True # For ProductReview mapping

class ReviewSummary(BaseModel):
    average_rating: float
    total_reviews: int
    rating_distribution: Dict[str, int]

class ProductReviewsData(BaseModel):
    reviews: List[ReviewItem]
    summary: ReviewSummary

class ProductReviewsResponse(BaseModel):
    success: bool
    data: ProductReviewsData

class SimilarProductsResponse(BaseModel):
    success: bool
    data: List[ProductItem]

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to map ORM Product to ProductItem Pydantic model
def map_product_to_product_item(product: Product, user: Optional[User] = None) -> ProductItem:
    # Cek status favorit jika user ada
    is_favorited = False
    if user:
        is_favorited = db.query(Favorite).filter(
            Favorite.user_id == user.id,
            Favorite.product_id == product.id
        ).first() is not None

    return ProductItem(
        id=product.id,
        name=product.name,
        price_per_day=product.price_per_day,
        original_price=product.original_price,
        discount_percentage=product.discount_percentage,
        rating=product.rating,
        review_count=product.review_count,
        image_url=product.images[0].image_url if product.images else "",
        is_favorited=is_favorited
    )

# Endpoint: GET /products
@router.get("", response_model=ProductListResponse)
def get_products(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    sort_by: Optional[str] = Query("popular", regex="^(price_asc|price_desc|rating|popular)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    query = db.query(Product).options(joinedload(Product.images))

    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if min_price is not None:
        query = query.filter(Product.price_per_day >= min_price)
    if max_price is not None:
        query = query.filter(Product.price_per_day <= max_price)

    # Sorting
    if sort_by == "price_asc":
        query = query.order_by(asc(Product.price_per_day))
    elif sort_by == "price_desc":
        query = query.order_by(desc(Product.price_per_day))
    elif sort_by == "rating":
        query = query.order_by(desc(Product.rating))
    elif sort_by == "popular":
        # Assuming 'popular' means high review count or rating for now
        query = query.order_by(desc(Product.review_count), desc(Product.rating))

    # Pagination
    total_items = query.count()
    total_pages = (total_items + limit - 1) // limit
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()

    product_items = [map_product_to_product_item(p, user) for p in products]

    pagination = Pagination(
        current_page=page,
        total_pages=total_pages,
        total_items=total_items,
        has_next=page < total_pages,
        has_prev=page > 1
    )

    return {"success": True, "data": {"products": product_items, "pagination": pagination}}

# Endpoint: GET /products/{product_id}
@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product_detail(
    product_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user)
):
    product = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.images)
    ).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Cek status favorit
    is_favorited = False
    if user:
        is_favorited = db.query(Favorite).filter(
            Favorite.user_id == user.id,
            Favorite.product_id == product.id
        ).first() is not None

    data = ProductDetailData(
        id=product.id,
        name=product.name,
        description=product.description,
        price_per_day=product.price_per_day,
        original_price=product.original_price,
        discount_percentage=product.discount_percentage,
        deposit_amount=product.deposit_amount,
        rating=product.rating,
        review_count=product.review_count,
        stock_quantity=product.stock_quantity,
        category=CategoryShort.from_orm(product.category) if product.category else None,
        images=[ProductImageItem.from_orm(img) for img in product.images],
        is_favorited=is_favorited
    )

    return {"success": True, "data": data}

# Endpoint: GET /products/{product_id}/reviews
@router.get("/{product_id}/reviews", response_model=ProductReviewsResponse)
def get_product_reviews(
    product_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50)
):
    # Get reviews with pagination
    offset = (page - 1) * limit
    reviews = (
        db.query(ProductReview)
        .filter(ProductReview.product_id == product_id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Calculate summary statistics
    total_reviews = db.query(ProductReview).filter(ProductReview.product_id == product_id).count()
    average_rating_result = db.query(func.avg(ProductReview.rating)).filter(ProductReview.product_id == product_id).scalar()
    average_rating = round(average_rating_result, 1) if average_rating_result is not None else 0.0

    rating_distribution_result = (
        db.query(ProductReview.rating, func.count(ProductReview.rating))
        .filter(ProductReview.product_id == product_id)
        .group_by(ProductReview.rating)
        .all()
    )

    rating_distribution = {str(r): count for r, count in rating_distribution_result}
    # Ensure all ratings 1-5 are present in the dict, even if count is 0
    for i in range(1, 6):
        if str(i) not in rating_distribution:
            rating_distribution[str(i)] = 0

    review_items = []
    for r in reviews:
        # Parse images string back to list
        try:
            images_list = json.loads(r.images)
        except (json.JSONDecodeError, TypeError):
            images_list = []

        review_items.append(ReviewItem(
            id=r.id,
            user=ReviewUser(name=r.user_name, profile_picture=r.user_profile_picture),
            rating=r.rating,
            comment=r.comment,
            images=images_list,
            created_at=r.created_at
        ))

    summary = ReviewSummary(
        average_rating=average_rating,
        total_reviews=total_reviews,
        rating_distribution=rating_distribution
    )

    return {"success": True, "data": {"reviews": review_items, "summary": summary}}

# Endpoint: GET /products/{product_id}/similar
@router.get("/{product_id}/similar", response_model=SimilarProductsResponse)
def get_similar_products(
    product_id: int = Path(..., ge=1),
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user)
):
    # Find the category of the current product
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        # If product not found, maybe return empty list or 404? Let's return empty for similar.
        return {"success": True, "data": []}

    # Find products in the same category, excluding the current product
    similar_products = (
        db.query(Product).options(joinedload(Product.images))
        .filter(Product.category_id == product.category_id)
        .filter(Product.id != product_id)
        .limit(limit)
        .all()
    )

    similar_products = [map_product_to_product_item(p, user) for p in similar_products]

    return {"success": True, "data": similar_products} 