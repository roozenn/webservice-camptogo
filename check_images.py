from db import SessionLocal
from models import ProductImage

db = SessionLocal()
images = db.query(ProductImage).all()

print("Data gambar produk:")
for img in images:
    print(f"Product {img.product_id}: {img.image_url}")

db.close() 