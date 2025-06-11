from db import SessionLocal
from models import (User, Banner, Category, Product, ProductImage, ProductReview, Favorite, Cart, Address, Coupon, PaymentMethod, Order, OrderItem, OrderTimeline)
from datetime import datetime, timedelta
from auth import get_password_hash
import random, json

# Base URL untuk gambar
IMAGE_BASE_URL = "https://raw.githubusercontent.com/roozenn/camp_to_go/refs/heads/main/lib/image/"
DUMMY_IMAGE_URL = "https://dummyimage.com/400x400/eee/333"

# Seed User
users = [
    User(
        full_name="Budi Santoso",
        email="budi@example.com",
        hashed_password=get_password_hash("password123"),
        profile_picture=DUMMY_IMAGE_URL,
        username="budi",
        gender="male",
        date_of_birth="1990-01-01",
        phone_number="081234567890"
    ),
    User(
        full_name="Siti Aminah",
        email="siti@example.com",
        hashed_password=get_password_hash("password123"),
        profile_picture=DUMMY_IMAGE_URL,
        username="siti",
        gender="female",
        date_of_birth="1992-05-10",
        phone_number="081298765432"
    ),
    User(
        full_name="Andi Pratama",
        email="andi@example.com",
        hashed_password=get_password_hash("password123"),
        profile_picture=DUMMY_IMAGE_URL,
        username="andi",
        gender="male",
        date_of_birth="1995-03-15",
        phone_number="081234567891"
    ),
    User(
        full_name="Dewi Lestari",
        email="dewi@example.com",
        hashed_password=get_password_hash("password123"),
        profile_picture=DUMMY_IMAGE_URL,
        username="dewi",
        gender="female",
        date_of_birth="1993-07-22",
        phone_number="081298765433"
    ),
    User(
        full_name="Rizky Hidayat",
        email="rizky@example.com",
        hashed_password=get_password_hash("password123"),
        profile_picture=DUMMY_IMAGE_URL,
        username="rizky",
        gender="male",
        date_of_birth="1991-11-11",
        phone_number="081234567892"
    ),
    User(
        full_name="Putri Ayu",
        email="putri@example.com",
        hashed_password=get_password_hash("password123"),
        profile_picture=DUMMY_IMAGE_URL,
        username="putri",
        gender="female",
        date_of_birth="1994-09-09",
        phone_number="081298765434"
    ),
    User(
        full_name="Agus Salim",
        email="agus@example.com",
        hashed_password=get_password_hash("password123"),
        profile_picture=DUMMY_IMAGE_URL,
        username="agus",
        gender="male",
        date_of_birth="1989-12-30",
        phone_number="081234567893"
    ),
    User(
        full_name="Maya Sari",
        email="maya@example.com",
        hashed_password=get_password_hash("password123"),
        profile_picture=DUMMY_IMAGE_URL,
        username="maya",
        gender="female",
        date_of_birth="1996-06-06",
        phone_number="081298765435"
    ),
    User(
        full_name="Fajar Nugroho",
        email="fajar@example.com",
        hashed_password=get_password_hash("password123"),
        profile_picture=DUMMY_IMAGE_URL,
        username="fajar",
        gender="male",
        date_of_birth="1997-02-18",
        phone_number="081234567894"
    ),
    User(
        full_name="Lina Marlina",
        email="lina@example.com",
        hashed_password=get_password_hash("password123"),
        profile_picture=DUMMY_IMAGE_URL,
        username="lina",
        gender="female",
        date_of_birth="1998-08-25",
        phone_number="081298765436"
    ),
]

# Seed Banner
banners = [
    Banner(title="Diskon Musim Panas", description="Dapatkan diskon hingga 50%", image_url=f"{IMAGE_BASE_URL}promo-3plus1.webp", link_url="https://example.com/promo1"),
    Banner(title="Promo Akhir Tahun", description="Sewa alat camping murah!", image_url=f"{IMAGE_BASE_URL}promo-pakethemat.webp", link_url="https://example.com/promo2")
]

# Seed Category
categories = [
    Category(name="Tenda", description="Berbagai jenis tenda camping", icon_url=DUMMY_IMAGE_URL),
    Category(name="Alat Tidur", description="Perlengkapan tidur outdoor: kasur, matras, sleeping bag", icon_url=DUMMY_IMAGE_URL),
    Category(name="Masak", description="Peralatan masak dan kompor camping", icon_url=DUMMY_IMAGE_URL),
    Category(name="Sepatu", description="Sepatu gunung dan outdoor", icon_url=DUMMY_IMAGE_URL),
    Category(name="Tas", description="Tas carrier, daypack, dan tas outdoor lainnya", icon_url=DUMMY_IMAGE_URL),
]

# Seed Product
products = [
    # 4 Produk Tenda
    Product(
        name="Tenda Eiger Mountain Dome 4P",
        description="Tenda dome kapasitas 4 orang, bahan waterproof, cocok untuk keluarga. Brand: Eiger.",
        price_per_day=90000,
        original_price=120000,
        discount_percentage=25,
        deposit_amount=200000,
        rating=4.7,
        review_count=8,
        stock_quantity=5,
        category_id=1
    ),
    Product(
        name="Tenda Consina Magnum 2P",
        description="Tenda ringan untuk 2 orang, mudah dipasang, ventilasi optimal. Brand: Consina.",
        price_per_day=65000,
        original_price=80000,
        discount_percentage=18,
        deposit_amount=150000,
        rating=4.5,
        review_count=5,
        stock_quantity=7,
        category_id=1
    ),
    Product(
        name="Tenda Rei Adventure 3P",
        description="Tenda 3 orang, double layer, anti bocor, cocok untuk pendakian musim hujan. Brand: Rei.",
        price_per_day=80000,
        original_price=95000,
        discount_percentage=15,
        deposit_amount=180000,
        rating=4.6,
        review_count=6,
        stock_quantity=6,
        category_id=1
    ),
    Product(
        name="Tenda Naturehike Cloud Up 2P",
        description="Tenda ultralight 2 orang, frame aluminium, sangat ringan untuk hiking. Brand: Naturehike.",
        price_per_day=100000,
        original_price=130000,
        discount_percentage=23,
        deposit_amount=220000,
        rating=4.8,
        review_count=10,
        stock_quantity=4,
        category_id=1
    ),
    # 4 Produk Kasur Camping (Alat Tidur)
    Product(
        name="Matras Angin Naturehike Ultralight",
        description="Matras angin ringan, mudah dibawa, cocok untuk camping dan hiking. Brand: Naturehike.",
        price_per_day=30000,
        original_price=40000,
        discount_percentage=25,
        deposit_amount=60000,
        rating=4.7,
        review_count=7,
        stock_quantity=10,
        category_id=2
    ),
    Product(
        name="Kasur Lipat Eiger Comfort",
        description="Kasur lipat busa, empuk dan mudah dilipat, cocok untuk camping keluarga. Brand: Eiger.",
        price_per_day=35000,
        original_price=45000,
        discount_percentage=22,
        deposit_amount=70000,
        rating=4.6,
        review_count=5,
        stock_quantity=8,
        category_id=2
    ),
    Product(
        name="Matras Gulung Consina Trekking",
        description="Matras gulung, bahan PE foam, ringan dan tahan air. Brand: Consina.",
        price_per_day=20000,
        original_price=25000,
        discount_percentage=20,
        deposit_amount=50000,
        rating=4.5,
        review_count=4,
        stock_quantity=12,
        category_id=2
    ),
    Product(
        name="Kasur Angin Bestway Double",
        description="Kasur angin double size, nyaman untuk 2 orang, pompa manual. Brand: Bestway.",
        price_per_day=40000,
        original_price=55000,
        discount_percentage=27,
        deposit_amount=80000,
        rating=4.8,
        review_count=9,
        stock_quantity=6,
        category_id=2
    ),
    # 4 Produk Kompor (Masak)
    Product(
        name="Kompor Portable Hi-Cook X3",
        description="Kompor gas portable, api biru stabil, mudah dibawa. Brand: Hi-Cook.",
        price_per_day=25000,
        original_price=35000,
        discount_percentage=28,
        deposit_amount=50000,
        rating=4.7,
        review_count=8,
        stock_quantity=10,
        category_id=3
    ),
    Product(
        name="Kompor Lipat Fire Maple FMS-300T",
        description="Kompor lipat super ringan, bahan titanium, cocok untuk ultralight hiking. Brand: Fire Maple.",
        price_per_day=35000,
        original_price=45000,
        discount_percentage=22,
        deposit_amount=70000,
        rating=4.8,
        review_count=12,
        stock_quantity=7,
        category_id=3
    ),
    Product(
        name="Kompor Camping BRS-3000T",
        description="Kompor mini, sangat ringan, efisien bahan bakar. Brand: BRS.",
        price_per_day=20000,
        original_price=30000,
        discount_percentage=33,
        deposit_amount=40000,
        rating=4.6,
        review_count=6,
        stock_quantity=9,
        category_id=3
    ),
    Product(
        name="Kompor Dua Tungku Winn Gas",
        description="Kompor dua tungku, cocok untuk camping keluarga, mudah digunakan. Brand: Winn Gas.",
        price_per_day=40000,
        original_price=55000,
        discount_percentage=27,
        deposit_amount=90000,
        rating=4.7,
        review_count=7,
        stock_quantity=5,
        category_id=3
    ),
    # 4 Produk Sepatu
    Product(
        name="Sepatu Gunung Eiger Ventura Mid",
        description="Sepatu gunung mid cut, sol Vibram, tahan air, nyaman untuk trekking. Brand: Eiger.",
        price_per_day=50000,
        original_price=70000,
        discount_percentage=29,
        deposit_amount=120000,
        rating=4.8,
        review_count=11,
        stock_quantity=8,
        category_id=4
    ),
    Product(
        name="Sepatu Hiking Consina Trailblazer",
        description="Sepatu hiking ringan, grip kuat, cocok untuk jalur berbatu. Brand: Consina.",
        price_per_day=45000,
        original_price=60000,
        discount_percentage=25,
        deposit_amount=100000,
        rating=4.7,
        review_count=9,
        stock_quantity=10,
        category_id=4
    ),
    Product(
        name="Sepatu Outdoor Rei Summit Pro",
        description="Sepatu outdoor, bahan breathable, anti slip, cocok untuk segala medan. Brand: Rei.",
        price_per_day=48000,
        original_price=65000,
        discount_percentage=26,
        deposit_amount=110000,
        rating=4.6,
        review_count=7,
        stock_quantity=7,
        category_id=4
    ),
    Product(
        name="Sepatu Hiking Columbia Redmond",
        description="Sepatu hiking waterproof, ringan dan nyaman, cocok untuk hiking panjang. Brand: Columbia.",
        price_per_day=60000,
        original_price=80000,
        discount_percentage=25,
        deposit_amount=130000,
        rating=4.9,
        review_count=13,
        stock_quantity=6,
        category_id=4
    ),
    # 4 Produk Tas
    Product(
        name="Tas Carrier Eiger 60L",
        description="Tas carrier kapasitas 60 liter, frame aluminium, cocok untuk ekspedisi. Brand: Eiger.",
        price_per_day=55000,
        original_price=75000,
        discount_percentage=27,
        deposit_amount=120000,
        rating=4.8,
        review_count=10,
        stock_quantity=8,
        category_id=5
    ),
    Product(
        name="Tas Daypack Consina Centurion 30L",
        description="Tas daypack 30 liter, banyak kompartemen, cocok untuk hiking harian. Brand: Consina.",
        price_per_day=35000,
        original_price=50000,
        discount_percentage=30,
        deposit_amount=70000,
        rating=4.7,
        review_count=8,
        stock_quantity=10,
        category_id=5
    ),
    Product(
        name="Tas Gunung Rei Adventure 45L",
        description="Tas gunung 45 liter, bahan kuat, rain cover included. Brand: Rei.",
        price_per_day=40000,
        original_price=60000,
        discount_percentage=33,
        deposit_amount=90000,
        rating=4.6,
        review_count=7,
        stock_quantity=7,
        category_id=5
    ),
    Product(
        name="Tas Carrier Osprey Atmos AG 65L",
        description="Tas carrier premium, sistem ventilasi anti pegal, kapasitas 65L. Brand: Osprey.",
        price_per_day=80000,
        original_price=120000,
        discount_percentage=33,
        deposit_amount=200000,
        rating=4.9,
        review_count=15,
        stock_quantity=4,
        category_id=5
    ),
]

# Seed ProductImage
product_images = [
    # Tenda
    ProductImage(product_id=1, image_url=f"{IMAGE_BASE_URL}tenda1.webp", is_primary=True),
    ProductImage(product_id=1, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=1, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    ProductImage(product_id=2, image_url=f"{IMAGE_BASE_URL}tenda2.webp", is_primary=True),
    ProductImage(product_id=2, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=2, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    ProductImage(product_id=3, image_url=f"{IMAGE_BASE_URL}tenda3.webp", is_primary=True),
    ProductImage(product_id=3, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=3, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    ProductImage(product_id=4, image_url=f"{IMAGE_BASE_URL}tenda4.webp", is_primary=True),
    ProductImage(product_id=4, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=4, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    # Kasur/Alat Tidur
    ProductImage(product_id=5, image_url=f"{IMAGE_BASE_URL}kasur1.webp", is_primary=True),
    ProductImage(product_id=5, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=5, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    ProductImage(product_id=6, image_url=f"{IMAGE_BASE_URL}kasur2.webp", is_primary=True),
    ProductImage(product_id=6, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=6, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    ProductImage(product_id=7, image_url=f"{IMAGE_BASE_URL}kasur3.webp", is_primary=True),
    ProductImage(product_id=7, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=7, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    ProductImage(product_id=8, image_url=f"{IMAGE_BASE_URL}kasur4.webp", is_primary=True),
    ProductImage(product_id=8, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=8, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    # Kompor
    ProductImage(product_id=9, image_url=f"{IMAGE_BASE_URL}kompor1.webp", is_primary=True),
    ProductImage(product_id=9, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=9, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    ProductImage(product_id=10, image_url=f"{IMAGE_BASE_URL}kompor2.webp", is_primary=True),
    ProductImage(product_id=10, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=10, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    ProductImage(product_id=11, image_url=f"{IMAGE_BASE_URL}kompor3.webp", is_primary=True),
    ProductImage(product_id=11, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=11, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    ProductImage(product_id=12, image_url=f"{IMAGE_BASE_URL}kompor4.webp", is_primary=True),
    ProductImage(product_id=12, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=12, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    # Sepatu
    ProductImage(product_id=13, image_url=f"{IMAGE_BASE_URL}sepatu1.webp", is_primary=True),
    ProductImage(product_id=13, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=13, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    ProductImage(product_id=14, image_url=f"{IMAGE_BASE_URL}sepatu2.webp", is_primary=True),
    ProductImage(product_id=14, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=14, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    ProductImage(product_id=15, image_url=f"{IMAGE_BASE_URL}sepatu3.webp", is_primary=True),
    ProductImage(product_id=15, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=15, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    ProductImage(product_id=16, image_url=f"{IMAGE_BASE_URL}sepatu4.webp", is_primary=True),
    ProductImage(product_id=16, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=16, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    # Tas
    ProductImage(product_id=17, image_url=f"{IMAGE_BASE_URL}tas1.webp", is_primary=True),
    ProductImage(product_id=17, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=17, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    ProductImage(product_id=18, image_url=f"{IMAGE_BASE_URL}tas2.webp", is_primary=True),
    ProductImage(product_id=18, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=18, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    ProductImage(product_id=19, image_url=f"{IMAGE_BASE_URL}tas3.webp", is_primary=True),
    ProductImage(product_id=19, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=19, image_url=DUMMY_IMAGE_URL, is_primary=False),
    
    ProductImage(product_id=20, image_url=f"{IMAGE_BASE_URL}tas4.jpg", is_primary=True),
    ProductImage(product_id=20, image_url=DUMMY_IMAGE_URL, is_primary=False),
    ProductImage(product_id=20, image_url=DUMMY_IMAGE_URL, is_primary=False),
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

# Buat 2 order, masing-masing user 1 order, 1 produk per order (biarkan untuk contoh order)
for i, user in enumerate(users[:2], start=1):
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
        user_profile_picture=DUMMY_IMAGE_URL,
        rating=5 if i == 1 else 4,
        comment="Barang bagus!" if i == 1 else "Sangat nyaman.",
        images=json.dumps([DUMMY_IMAGE_URL, DUMMY_IMAGE_URL, DUMMY_IMAGE_URL]),
        created_at=datetime.utcnow() - timedelta(days=1)
    ))

# Tambahkan minimal 2 review per produk dari user berbeda
review_comments = [
    "Barang sangat memuaskan, sesuai deskripsi.",
    "Kondisi produk bagus, pengiriman cepat.",
    "Sangat membantu untuk camping, recommended!",
    "Harga sewa terjangkau, kualitas oke.",
    "Akan sewa lagi kalau butuh.",
    "Pelayanan ramah, produk bersih.",
    "Produk original, tidak mengecewakan.",
    "Pengalaman sewa menyenangkan.",
    "Barang mudah digunakan, sesuai kebutuhan.",
    "Sesuai ekspektasi, mantap!"
]

for pid in range(1, 21):
    for ridx in range(2):
        uid = ((pid + ridx) % 10) + 1  # user_id bergantian dari 1-10
        product_reviews.append(ProductReview(
            product_id=pid,
            user_id=uid,
            order_id=None,
            user_name=users[uid-1].full_name,
            user_profile_picture=DUMMY_IMAGE_URL,
            rating=random.choice([4, 5]),
            comment=review_comments[(pid + ridx) % len(review_comments)],
            images=json.dumps([DUMMY_IMAGE_URL, DUMMY_IMAGE_URL, DUMMY_IMAGE_URL]),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
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