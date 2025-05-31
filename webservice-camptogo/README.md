# CampToGo Webservice

## Cara Menjalankan

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Jalankan server:
   ```bash
   uvicorn main:app --reload
   ```

## Endpoints

### Auth
- POST /auth/register — Register user baru
- POST /auth/login — Login user
- POST /auth/refresh — Refresh token JWT
- POST /auth/logout — Logout (dummy)

### Home
- GET /home/banners — Daftar banner promosi
- GET /home/categories — Daftar kategori produk
- GET /home/recommendations/beginner — Rekomendasi produk untuk pemula
- GET /home/recommendations/popular — Rekomendasi produk populer

### Products
- GET /products — List produk (filter, sort, pagination)
- GET /products/{product_id} — Detail produk
- GET /products/{product_id}/reviews — List review produk
- GET /products/{product_id}/similar — Produk serupa

### Search
- GET /search — Cari produk (query, kategori, pagination)
- GET /search/suggestions — Saran pencarian produk

### Favorites
- GET /favorites — Daftar produk favorit user (perlu login)
- POST /favorites/{product_id} — Tambah produk ke favorit (perlu login)
- DELETE /favorites/{product_id} — Hapus produk dari favorit (perlu login)

Semua endpoint ada di file `auth.py` dan sudah sesuai dengan spesifikasi permintaan. 