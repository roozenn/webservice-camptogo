from db import SessionLocal
from models import Banner, Category, Product, ProductImage, ProductReview

def clear_all():
    db = SessionLocal()
    try:
        db.query(ProductReview).delete()
        db.query(ProductImage).delete()
        db.query(Product).delete()
        db.query(Category).delete()
        db.query(Banner).delete()
        db.commit()
        print("Semua data lama sudah dihapus.")
    finally:
        db.close()

if __name__ == "__main__":
    clear_all() 