from db import SessionLocal
from models import (User, Banner, Category, Product, ProductImage, ProductReview, Favorite, Cart, Address, Coupon, PaymentMethod, Order, OrderItem, OrderTimeline)
from datetime import datetime, timedelta
from auth import get_password_hash
import random, json

# Seed User
users = [
    User(
        full_name="Budi Santoso",
        email="budi@example.com",
        hashed_password=get_password_hash("password123"),
        profile_picture="",
        username="budi",
        gender="male",
        date_of_birth="1990-01-01",
        phone_number="081234567890"
    ),
    User(
        full_name="Siti Aminah",
        email="siti@example.com",
        hashed_password=get_password_hash("password123"),
        profile_picture="",
        username="siti",
        gender="female",
        date_of_birth="1992-05-10",
        phone_number="081298765432"
    )
]

# Seed Banner
banners = [
    Banner(title="Diskon Musim Panas", description="Dapatkan diskon hingga 50%", image_url="https://dummyimage.com/600x200/eee/333", link_url="https://example.com/promo1"),
    Banner(title="Promo Akhir Tahun", description="Sewa alat camping murah!", image_url="https://dummyimage.com/600x200/eee/333", link_url="https://example.com/promo2")
]

# Seed Category
categories = [
    Category(name="Tenda", description="Berbagai jenis tenda camping", icon_url="https://dummyimage.com/100x100/eee/333"),
    Category(name="Sleeping Bag", description="Aneka sleeping bag hangat", icon_url="https://dummyimage.com/100x100/eee/333")
]

# Seed Product
products = [
    Product(
        name="Tenda Gunung 2P",
        description="Tenda kapasitas 2 orang, cocok untuk hiking.",
        price_per_day=50000,
        original_price=60000,
        discount_percentage=10,
        deposit_amount=100000,
        rating=4.5,
        review_count=2,
        stock_quantity=10,
        category_id=1
    ),
    Product(
        name="Sleeping Bag Hangat",
        description="Sleeping bag nyaman dan hangat.",
        price_per_day=20000,
        original_price=25000,
        discount_percentage=5,
        deposit_amount=50000,
        rating=5.0,
        review_count=1,
        stock_quantity=15,
        category_id=2
    )
]

# Seed ProductImage
product_images = [
    ProductImage(product_id=1, image_url="https://dummyimage.com/400x400/eee/333", is_primary=True),
    ProductImage(product_id=2, image_url="https://dummyimage.com/400x400/eee/333", is_primary=True)
]

# Seed Coupon
coupons = [
    Coupon(code="DISKON10", discount_amount=10000, is_active=True, valid_until=None, description="Diskon 10 ribu tanpa kadaluarsa"),
    Coupon(code="PROMO50", discount_amount=50000, is_active=True, valid_until=datetime(2099, 12, 31), description="Promo 50 ribu sampai 2099"),
    Coupon(code="EXPIRED1", discount_amount=15000, is_active=True, valid_until=datetime(2020, 1, 1), description="Kupon kadaluarsa"),
    Coupon(code="NONAKTIF", discount_amount=20000, is_active=False, valid_until=None, description="Kupon tidak aktif"),
]

# Seed Address
addresses = [
    Address(user_id=1, recipient_name="Budi Santoso", full_address="Jl. Mawar No. 1, Jakarta", phone_number="081234567890", is_default=True),
    Address(user_id=2, recipient_name="Siti Aminah", full_address="Jl. Melati No. 2, Bandung", phone_number="081298765432", is_default=True)
]

# Seed PaymentMethod
payment_methods = [
    PaymentMethod(user_id=1, method_type="bank_transfer", provider_name="BCA", account_number="1234567890", account_name="Budi Santoso", is_default=True),
    PaymentMethod(user_id=2, method_type="ewallet", provider_name="OVO", account_number="081298765432", account_name="Siti Aminah", is_default=True)
]

# Seed Cart
carts = [
    Cart(user_id=1, product_id=1, start_date="2024-07-01", end_date="2024-07-03", quantity=1),
    Cart(user_id=2, product_id=2, start_date="2024-07-02", end_date="2024-07-04", quantity=2)
]

# Seed Favorite
favorites = [
    Favorite(user_id=1, product_id=2),
    Favorite(user_id=2, product_id=1)
]

# Seed Order, OrderItem, OrderTimeline
orders = []
order_items = []
order_timelines = []
product_reviews = []

# Buat 2 order, masing-masing user 1 order, 1 produk per order
for i, user in enumerate(users, start=1):
    order = Order(
        user_id=i,
        address_id=i,
        payment_method_id=i,
        coupon_id=1 if i == 1 else None,
        order_number=f"ORD2024070{i}000{i}",
        status="pending",
        notes="",
        total_amount=120000 if i == 1 else 70000,
        discount_amount=10000 if i == 1 else 0,
        deposit_total=100000 if i == 1 else 50000,
        created_at=datetime.utcnow() - timedelta(days=2),
        shipping_date="2024-07-01",
        return_date="2024-07-03"
    )
    orders.append(order)
    order_item = OrderItem(
        order_id=i,
        product_id=i,
        quantity=1,
        start_date="2024-07-01",
        end_date="2024-07-03",
        subtotal=60000 if i == 1 else 40000,
        deposit_subtotal=100000 if i == 1 else 50000
    )
    order_items.append(order_item)
    order_timelines.append(OrderTimeline(order_id=i, status="pending", description="Pesanan dibuat", created_at=datetime.utcnow() - timedelta(days=2)))
    # Seed ProductReview (1 review per order item)
    product_reviews.append(ProductReview(
        product_id=i,
        user_id=i,
        order_id=i,
        user_name=user.full_name,
        user_profile_picture=user.profile_picture,
        rating=5 if i == 1 else 4,
        comment="Barang bagus!" if i == 1 else "Sangat nyaman.",
        images=json.dumps(["https://dummyimage.com/400x400/eee/333"]),
        created_at=datetime.utcnow() - timedelta(days=1)
    ))

def seed():
    db = SessionLocal()
    try:
        db.query(OrderTimeline).delete()
        db.query(OrderItem).delete()
        db.query(Order).delete()
        db.query(ProductReview).delete()
        db.query(Favorite).delete()
        db.query(Cart).delete()
        db.query(PaymentMethod).delete()
        db.query(Address).delete()
        db.query(Coupon).delete()
        db.query(ProductImage).delete()
        db.query(Product).delete()
        db.query(Category).delete()
        db.query(Banner).delete()
        db.query(User).delete()
        db.commit()

        db.add_all(users)
        db.commit()
        db.add_all(banners)
        db.add_all(categories)
        db.commit()
        db.add_all(products)
        db.commit()
        db.add_all(product_images)
        db.commit()
        db.add_all(coupons)
        db.commit()
        db.add_all(addresses)
        db.commit()
        db.add_all(payment_methods)
        db.commit()
        db.add_all(carts)
        db.commit()
        db.add_all(favorites)
        db.commit()
        db.add_all(orders)
        db.commit()
        db.add_all(order_items)
        db.commit()
        db.add_all(order_timelines)
        db.commit()
        db.add_all(product_reviews)
        db.commit()
        print("Seed data selesai!")
    finally:
        db.close()

if __name__ == "__main__":
    seed() 