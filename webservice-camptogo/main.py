from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from auth import router as auth_router
from db import Base, engine
import models
from home import router as home_router
from products import router as products_router
from favorites import router as favorites_router
from search import router as search_router
from cart import router as cart_router
from addresses import router as addresses_router
from payment_methods import router as payment_methods_router
from orders import router as orders_router
from reviews import router as reviews_router
from profile import router as profile_router

app = FastAPI(title="CampToGo Webservice")

# Inisialisasi DB (buat tabel jika belum ada)
Base.metadata.create_all(bind=engine)

# Mount static files directory to serve uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth_router)
app.include_router(home_router)
app.include_router(products_router)
app.include_router(favorites_router)
app.include_router(search_router)
app.include_router(cart_router)
app.include_router(addresses_router)
app.include_router(payment_methods_router)
app.include_router(orders_router)
app.include_router(reviews_router)
app.include_router(profile_router) 