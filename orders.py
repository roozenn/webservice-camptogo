from fastapi import APIRouter, Depends, HTTPException, status, Path, Query, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from models import Order, OrderItem, OrderTimeline, Cart, Product, Address, PaymentMethod, Coupon, User
from auth import get_db, get_current_user
from pydantic import BaseModel
import random, string
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["Orders"])

# Response Models
class OrderItemProduct(BaseModel):
    id: int
    name: str
    image_url: str
    class Config:
        from_attributes = True

class OrderItemDetail(BaseModel):
    product: OrderItemProduct
    quantity: int
    start_date: str
    end_date: str
    subtotal: float
    deposit_subtotal: float
    class Config:
        from_attributes = True

class OrderAddress(BaseModel):
    recipient_name: str
    full_address: str
    phone_number: str
    class Config:
        from_attributes = True

class PaymentSummary(BaseModel):
    subtotal: float
    deposit_total: float
    discount_amount: float
    total_amount: float

class TimelineItem(BaseModel):
    status: str
    description: str
    created_at: datetime
    class Config:
        from_attributes = True

class OrderDetailResponseData(BaseModel):
    id: int
    order_number: str
    status: str
    items: List[OrderItemDetail]
    address: OrderAddress
    payment_summary: PaymentSummary
    timeline: List[TimelineItem]
    class Config:
        from_attributes = True

class OrderDetailResponse(BaseModel):
    success: bool
    data: OrderDetailResponseData

class OrderListItem(BaseModel):
    id: int
    order_number: str
    status: str
    total_amount: float
    item_count: int
    created_at: datetime
    shipping_date: Optional[str]
    return_date: Optional[str]
    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    success: bool
    data: dict

class CreateOrderRequest(BaseModel):
    address_id: int
    payment_method_id: int
    coupon_code: Optional[str] = None
    notes: Optional[str] = ""

class CreateOrderResponse(BaseModel):
    success: bool
    message: str
    data: dict

class SimpleResponse(BaseModel):
    success: bool
    message: str

# Helper

def generate_order_number():
    return 'ORD' + datetime.utcnow().strftime('%Y%m%d%H%M%S') + ''.join(random.choices(string.digits, k=4))

def get_cart_for_order(user: User, db: Session):
    return db.query(Cart).filter(Cart.user_id == user.id).all()

def calc_order_totals(cart_items, coupon: Optional[Coupon]):
    subtotal = 0
    deposit_total = 0
    for item in cart_items:
        product = item.product
        days_count = (datetime.strptime(item.end_date, "%Y-%m-%d") - datetime.strptime(item.start_date, "%Y-%m-%d")).days + 1
        subtotal += product.price_per_day * days_count * item.quantity
        deposit_total += product.deposit_amount * item.quantity
    discount_amount = coupon.discount_amount if coupon else 0
    total_amount = max(subtotal + deposit_total - discount_amount, 0)
    return subtotal, deposit_total, discount_amount, total_amount

async def update_order_status_after_delay(order_id: int, db: Session):
    # Tunggu 30 detik
    await asyncio.sleep(30)
    
    # Ambil order dan update status
    order = db.query(Order).filter(Order.id == order_id).first()
    if order and order.status == "pending":
        order.status = "ongoing"
        timeline = OrderTimeline(
            order_id=order.id,
            status="ongoing",
            description="Pesanan dikonfirmasi dan sedang diproses",
            created_at=datetime.utcnow()
        )
        db.add(timeline)
        db.commit()

# Endpoint: POST /orders
@router.post("", response_model=CreateOrderResponse)
def create_order(req: CreateOrderRequest, background_tasks: BackgroundTasks, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_items = get_cart_for_order(user, db)
    if not cart_items:
        raise HTTPException(status_code=400, detail="Keranjang kosong")
    address = db.query(Address).filter(Address.id == req.address_id, Address.user_id == user.id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Alamat tidak ditemukan")
    payment_method = db.query(PaymentMethod).filter(PaymentMethod.id == req.payment_method_id, PaymentMethod.user_id == user.id).first()
    if not payment_method:
        raise HTTPException(status_code=404, detail="Metode pembayaran tidak ditemukan")
    coupon = None
    if req.coupon_code:
        coupon = db.query(Coupon).filter(Coupon.code == req.coupon_code, Coupon.is_active == True).first()
        if not coupon or (coupon.valid_until and coupon.valid_until < datetime.utcnow()):
            coupon = None
    subtotal, deposit_total, discount_amount, total_amount = calc_order_totals(cart_items, coupon)
    order_number = generate_order_number()
    order = Order(
        user_id=user.id,
        address_id=address.id,
        payment_method_id=payment_method.id,
        coupon_id=coupon.id if coupon else None,
        order_number=order_number,
        status="pending",
        notes=req.notes or "",
        total_amount=total_amount,
        discount_amount=discount_amount,
        deposit_total=deposit_total,
        shipping_date=cart_items[0].start_date if cart_items else None,
        return_date=cart_items[0].end_date if cart_items else None
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    # Simpan order items
    for item in cart_items:
        product = item.product
        days_count = (datetime.strptime(item.end_date, "%Y-%m-%d") - datetime.strptime(item.start_date, "%Y-%m-%d")).days + 1
        subtotal_item = product.price_per_day * days_count * item.quantity
        deposit_item = product.deposit_amount * item.quantity
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            start_date=item.start_date,
            end_date=item.end_date,
            subtotal=subtotal_item,
            deposit_subtotal=deposit_item
        )
        db.add(order_item)
    # Timeline
    timeline = OrderTimeline(
        order_id=order.id,
        status="pending",
        description="Pesanan dibuat",
        created_at=datetime.utcnow()
    )
    db.add(timeline)
    # Hapus cart
    for item in cart_items:
        db.delete(item)
    db.commit()
    
    # Tambahkan background task untuk update status setelah 30 detik
    background_tasks.add_task(update_order_status_after_delay, order.id, db)
    
    return {"success": True, "message": "Pesanan berhasil dibuat", "data": {"order_id": order.id, "order_number": order.order_number, "total_amount": order.total_amount}}

# Endpoint: GET /orders
@router.get("", response_model=OrderListResponse)
def get_orders(status: Optional[str] = Query(None), page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Order).filter(Order.user_id == user.id)
    if status:
        query = query.filter(Order.status == status)
    total_items = query.count()
    orders = query.order_by(Order.created_at.desc()).offset((page-1)*limit).limit(limit).all()
    result = []
    for o in orders:
        result.append(OrderListItem(
            id=o.id,
            order_number=o.order_number,
            status=o.status,
            total_amount=o.total_amount,
            item_count=len(o.items),
            created_at=o.created_at,
            shipping_date=o.shipping_date,
            return_date=o.return_date
        ))
    return {"success": True, "data": {"orders": result}}

# Endpoint: GET /orders/{order_id}
@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order_detail(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Log request
        logger.info(f"Fetching order detail for order_id: {order_id}, user_id: {user.id}")
        
        # Get order with basic relations first
        order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
        if not order:
            logger.warning(f"Order not found: order_id={order_id}, user_id={user.id}")
            raise HTTPException(status_code=404, detail="Order tidak ditemukan")
            
        # Load relations separately to better handle errors
        try:
            items = []
            for item in order.items:
                try:
                    product = item.product
                    image_url = product.images[0].image_url if product.images else ""
                    items.append(OrderItemDetail(
                        product=OrderItemProduct(id=product.id, name=product.name, image_url=image_url),
                        quantity=item.quantity,
                        start_date=item.start_date,
                        end_date=item.end_date,
                        subtotal=item.subtotal,
                        deposit_subtotal=item.deposit_subtotal
                    ))
                except Exception as e:
                    logger.error(f"Error processing order item: {str(e)}")
                    raise HTTPException(status_code=500, detail="Error memproses item pesanan")
            
            if not order.address:
                logger.error(f"Address not found for order: {order_id}")
                raise HTTPException(status_code=500, detail="Alamat tidak ditemukan")
                
            address = order.address
            payment_summary = PaymentSummary(
                subtotal=sum(i.subtotal for i in order.items),
                deposit_total=order.deposit_total,
                discount_amount=order.discount_amount,
                total_amount=order.total_amount
            )
            
            timeline = [TimelineItem(status=t.status, description=t.description, created_at=t.created_at) 
                       for t in order.timeline]
            
            data = OrderDetailResponseData(
                id=order.id,
                order_number=order.order_number,
                status=order.status,
                items=items,
                address=OrderAddress(
                    recipient_name=address.recipient_name,
                    full_address=address.full_address,
                    phone_number=address.phone_number
                ),
                payment_summary=payment_summary,
                timeline=timeline
            )
            
            logger.info(f"Successfully fetched order detail for order_id: {order_id}")
            return {"success": True, "data": data}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing order detail: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error memproses detail pesanan: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_order_detail: {str(e)}")
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal server")

# Endpoint: POST /orders/{order_id}/return
@router.post("/{order_id}/return", response_model=SimpleResponse)
def return_order(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order tidak ditemukan")
    if order.status != "ongoing":
        raise HTTPException(status_code=400, detail="Order tidak dalam status ongoing")
    order.status = "returned"
    timeline = OrderTimeline(
        order_id=order.id,
        status="returned",
        description="Barang dikembalikan oleh user",
        created_at=datetime.utcnow()
    )
    db.add(timeline)
    db.commit()
    return {"success": True, "message": "Pengembalian barang berhasil dikonfirmasi"} 