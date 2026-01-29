# 📊 Modern CMS - Python FastAPI Loyihasi Tahlili

> **Loyiha nomi:** Modern CMS  
> **Tahlil sanasi:** 2026-01-29  
> **Loyiha joylashuvi:** `/home/miracle/Code/dle19_0_nulled`

---

## 📋 Tezkor Ma'lumot

| Parametr | Qiymat |
|----------|--------|
| **Tizim nomi** | Modern CMS |
| **Versiya** | 1.0.0 |
| **Til/Framework** | Python 3.10+ / FastAPI |
| **Template Engine** | Jinja2 |
| **Database** | SQLite (aiosqlite) / PostgreSQL |
| **ORM** | SQLAlchemy (Async) |
| **Authentication** | JWT (python-jose) |

---

## 📁 Loyiha Tuzilishi

```
dle19_0_nulled/
├── 📂 app/                      # Asosiy application
│   ├── 📂 api/                  # REST API endpoints
│   │   ├── 📂 v1/               # API v1 versiyasi
│   │   │   ├── 📄 auth.py       # Autentifikatsiya
│   │   │   ├── 📄 users.py      # Foydalanuvchilar
│   │   │   ├── 📄 posts.py      # Postlar/Maqolalar
│   │   │   ├── 📄 categories.py # Kategoriyalar
│   │   │   └── 📄 comments.py   # Izohlar
│   │   └── 📄 deps.py           # Dependencies
│   ├── 📂 core/                 # Yadro funksiyalar
│   │   ├── 📄 config.py         # Sozlamalar
│   │   ├── 📄 database.py       # DB ulanish
│   │   └── 📄 security.py       # JWT & Password
│   ├── 📂 models/               # SQLAlchemy modellar
│   │   ├── 📄 user.py           # User, UserGroup, Favorite
│   │   ├── 📄 post.py           # Post, Tag, PostView, PostRating
│   │   ├── 📄 category.py       # Category
│   │   ├── 📄 comment.py        # Comment, CommentVote
│   │   └── 📄 cms.py            # StaticPage, Banner, Setting, Menu
│   ├── 📂 schemas/              # Pydantic schemalar
│   ├── 📂 services/             # Biznes logika
│   ├── 📂 utils/                # Yordamchi funksiyalar
│   ├── 📂 web/                  # Frontend routelar
│   │   ├── 📄 routes.py         # Public sahifalar
│   │   └── 📄 admin.py          # Admin panel
│   └── 📄 main.py               # FastAPI application
├── 📂 templates/                # Jinja2 templates
│   ├── 📂 admin/                # Admin panel templates
│   │   ├── 📄 base.html         # Admin layout
│   │   ├── 📄 dashboard.html    # Dashboard
│   │   ├── 📄 posts.html        # Postlar ro'yxati
│   │   ├── 📄 post_form.html    # Post yaratish/tahrirlash
│   │   ├── 📄 users.html        # Foydalanuvchilar
│   │   ├── 📄 categories.html   # Kategoriyalar
│   │   ├── 📄 comments.html     # Izohlar moderatsiyasi
│   │   ├── 📄 settings.html     # Sayt sozlamalari
│   │   └── 📄 pages.html        # Statik sahifalar
│   ├── 📂 auth/                 # Autentifikatsiya
│   │   ├── 📄 login.html        # Kirish sahifasi
│   │   └── 📄 register.html     # Ro'yxatdan o'tish
│   ├── 📄 base.html             # Asosiy layout
│   ├── 📄 home.html             # Bosh sahifa
│   ├── 📄 post_detail.html      # Post ko'rish
│   ├── 📄 category.html         # Kategoriya postlari
│   ├── 📄 tag.html              # Teg postlari
│   └── 📄 search.html           # Qidiruv natijalari
├── 📂 static/                   # Statik fayllar
├── 📂 uploads/                  # Yuklangan fayllar
├── 📂 migrations/               # Alembic migratsiyalar
├── 📂 tests/                    # Testlar
├── 📄 requirements.txt          # Python bog'liqliklari
├── 📄 .env                      # Muhit sozlamalari
├── 📄 run_dev.sh                # Dev server
├── 📄 run_prod.sh               # Prod server
├── 📄 Dockerfile                # Docker konfiguratsiya
└── 📄 docker-compose.yml        # Docker compose
```

---

## ⚙️ Texnik Arxitektura

### 🗄️ Ma'lumotlar Bazasi

- **DBMS:** SQLite (default) / PostgreSQL
- **ORM:** SQLAlchemy 2.0 (Async)
- **Connection:** `sqlite+aiosqlite:///./cms.db`

#### Asosiy Jadvallar:

| Jadval | Tavsif | Maydonlar |
|--------|--------|-----------|
| `users` | Foydalanuvchilar | id, username, email, password_hash, avatar, bio, group_id |
| `user_groups` | Foydalanuvchi guruhlari | id, name, permissions |
| `posts` | Maqolalar | id, title, slug, content, author_id, is_published, views_count |
| `categories` | Kategoriyalar | id, name, slug, parent_id, posts_count |
| `tags` | Teglar | id, name, slug, posts_count |
| `comments` | Izohlar | id, content, author_id, post_id, parent_id |
| `static_pages` | Statik sahifalar | id, name, slug, title, content |
| `settings` | Sayt sozlamalari | id, key, value, type, group |
| `banners` | Bannerlar | id, name, position, image_url, is_active |
| `menus` | Menyular | id, name, location, url, parent_id |

#### Aloqa Jadvallari:
- `post_categories` - Post va kategoriya ko'p-ko'pga aloqasi
- `post_tags` - Post va teg ko'p-ko'pga aloqasi
- `post_views` - Post ko'rishlar statistikasi
- `post_ratings` - Post reytinglari
- `comment_votes` - Izoh ovozlari
- `favorites` - Foydalanuvchi sevimli postlari

### 🔐 Autentifikatsiya Tizimi

| Komponent | Texnologiya | Tavsif |
|-----------|-------------|--------|
| **JWT Token** | python-jose | Access token (30 min) |
| **Refresh Token** | python-jose | 7 kun amal qiladi |
| **Password Hashing** | passlib[bcrypt] | Secure password storage |
| **Cookie Auth** | FastAPI | Web frontend uchun |

### 👥 Foydalanuvchi Guruhlari

| ID | Guruh | Ruxsatlar |
|----|-------|-----------|
| 1 | **Administrator** | To'liq kirish, admin panel |
| 2 | **User** | Faqat izoh yozish |
| 3 | **Editor** | Post yaratish/tahrirlash |
| 4 | **Moderator** | Kontent moderatsiyasi |

---

## 🌐 API Endpoints

### Autentifikatsiya (`/api/v1/auth`)

| Method | Endpoint | Tavsif |
|--------|----------|--------|
| POST | `/login` | Kirish (token olish) |
| POST | `/register` | Ro'yxatdan o'tish |
| POST | `/refresh` | Token yangilash |
| POST | `/logout` | Chiqish |

### Foydalanuvchilar (`/api/v1/users`)

| Method | Endpoint | Tavsif |
|--------|----------|--------|
| GET | `/me` | Joriy foydalanuvchi |
| PATCH | `/me` | Profil yangilash |
| POST | `/me/password` | Parol o'zgartirish |
| GET | `/{id}` | Foydalanuvchi ma'lumotlari |
| GET | `/` | Ro'yxat (admin) |

### Postlar (`/api/v1/posts`)

| Method | Endpoint | Tavsif |
|--------|----------|--------|
| GET | `/` | Postlar ro'yxati |
| GET | `/featured` | Featured postlar |
| GET | `/popular` | Ommabop postlar |
| GET | `/{id}` | Post ma'lumotlari |
| POST | `/` | Post yaratish |
| PATCH | `/{id}` | Post tahrirlash |
| DELETE | `/{id}` | Post o'chirish |
| POST | `/{id}/rate` | Post baholash |

### Kategoriyalar (`/api/v1/categories`)

| Method | Endpoint | Tavsif |
|--------|----------|--------|
| GET | `/` | Kategoriyalar ro'yxati |
| GET | `/tree` | Kategoriyalar daraxti |
| GET | `/tags` | Teglar ro'yxati |
| GET | `/tags/popular` | Ommabop teglar |

### Izohlar (`/api/v1/comments`)

| Method | Endpoint | Tavsif |
|--------|----------|--------|
| GET | `/post/{id}` | Post izohlari |
| POST | `/` | Izoh qo'shish |
| PATCH | `/{id}` | Izoh tahrirlash |
| DELETE | `/{id}` | Izoh o'chirish |
| POST | `/{id}/vote` | Ovoz berish |

---

## 🖥️ Admin Panel

### Mavjud Sahifalar

| Sahifa | URL | Holati |
|--------|-----|--------|
| **Dashboard** | `/admin` | ✅ To'liq ishlaydi |
| **Posts** | `/admin/posts` | ✅ To'liq ishlaydi |
| **Post Form** | `/admin/posts/new` | ✅ To'liq ishlaydi |
| **Users** | `/admin/users` | ✅ Ro'yxat ishlaydi |
| **Comments** | `/admin/comments` | ✅ Moderatsiya ishlaydi |
| **Categories** | `/admin/categories` | ✅ Ro'yxat ishlaydi |
| **Settings** | `/admin/settings` | ⚠️ UI bor, saqlash ishlamaydi |
| **Pages** | `/admin/pages` | ⚠️ UI bor, CRUD ishlamaydi |

### Dashboard Statistikalari

- 📝 Maqolalar soni
- 👥 Foydalanuvchilar soni
- 💬 Izohlar soni
- 👁️ Ko'rishlar soni

---

## 🎨 Frontend

### Mavjud Sahifalar

| Sahifa | URL | Tavsif |
|--------|-----|--------|
| **Bosh sahifa** | `/` | Featured post, so'nggi maqolalar |
| **Post** | `/post/{slug}` | To'liq maqola, izohlar |
| **Kategoriya** | `/category/{slug}` | Kategoriya postlari |
| **Teg** | `/tag/{slug}` | Teg postlari |
| **Qidiruv** | `/search?q=` | Qidiruv natijalari |
| **Kirish** | `/login` | Login sahifasi |
| **Ro'yxatdan o'tish** | `/register` | Registratsiya |

### Dizayn Xususiyatlari

- 🎨 Zamonaviy gradient hero section
- 📱 Responsive dizayn
- 🌙 Toza, professional ko'rinish
- 💬 Nested izohlar tizimi

---

## 📦 Bog'liqliklar (Dependencies)

| Kutubxona | Maqsadi |
|-----------|---------|
| **fastapi** | Web framework |
| **uvicorn[standard]** | ASGI server |
| **sqlalchemy** | ORM |
| **alembic** | Migratsiyalar |
| **aiosqlite** | Async SQLite driver |
| **python-jose[cryptography]** | JWT tokens |
| **passlib[bcrypt]** | Password hashing |
| **pydantic** | Data validation |
| **pydantic-settings** | Settings management |
| **jinja2** | Template engine |
| **python-multipart** | Form data |
| **aiofiles** | Async file operations |
| **python-slugify** | URL slugs |
| **email-validator** | Email validation |

---

## 🚀 Ishga Tushirish

### Minimal talablar

- **Python:** 3.10+
- **pip:** Latest

### O'rnatish qadamlari

1. **Virtual muhit yaratish**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Bog'liqliklarni o'rnatish**
   ```bash
   pip install -r requirements.txt
   ```

3. **Muhit sozlamalari**
   ```bash
   cp .env.example .env
   nano .env
   ```

4. **Ishga tushirish**
   ```bash
   ./run_dev.sh
   # yoki
   uvicorn app.main:app --reload
   ```

### Muhim URL manzillar

| Sahifa | URL |
|--------|-----|
| **Bosh sahifa** | `http://localhost:8000/` |
| **Admin Panel** | `http://localhost:8000/admin` |
| **API Docs** | `http://localhost:8000/docs` |
| **ReDoc** | `http://localhost:8000/redoc` |
| **Health** | `http://localhost:8000/health` |

---

## ⚠️ Tuzatish Kerak Bo'lgan Muammolar

### 1. 🔧 Settings sahifasi
> Settings sahifasida UI mavjud, lekin saqlash funksiyasi ishlamaydi. Database'ga yozish kerak.

**Fayl:** `app/web/admin.py` (337-345 qatorlar)
```python
@router.post("/settings")
async def admin_settings_save(request: Request, db: AsyncSession = Depends(get_db)):
    # TODO: Save settings to database
    return RedirectResponse("/admin/settings", status_code=302)
```

### 2. 🔧 Static Pages (Statik sahifalar)
> Pages boshqaruv sahifasida CRUD operatsiyalari to'liq ishlamaydi.

**Fayl:** `app/web/admin.py` (350-385 qatorlar)
```python
@router.get("/pages", response_class=HTMLResponse)
async def admin_pages(...):
    # TODO: Load pages from database
    pages = []
```

### 3. ⚠️ Eskirgan FastAPI sintaksisi
> `regex` parametri `pattern` ga o'zgartirilishi kerak.

**Fayl:** `app/api/v1/posts.py` (41-42 qatorlar)
```python
# ESKI:
sort_by: str = Query("created_at", regex="^...")
# YANGI:
sort_by: str = Query("created_at", pattern="^...")
```

### 4. 🛠️ Favicon yo'q
> Brauzer 404 xatosini ko'rsatadi.

**Yechim:** `/static/favicon.ico` faylini qo'shish

---

## 📊 Statistika

| Kategoriya | Soni |
|------------|------|
| **Python fayllar** | ~25 |
| **Template fayllar** | 17 |
| **API endpoints** | ~30 |
| **Database jadvallar** | 16 |
| **Default user groups** | 4 |

---

## ✅ Ishlayotgan Funksiyalar

- [x] JWT autentifikatsiya
- [x] Foydalanuvchi registratsiyasi
- [x] Login/Logout
- [x] Post yaratish/tahrirlash/o'chirish
- [x] Kategoriyalar boshqaruvi
- [x] Izohlar tizimi (nested)
- [x] Izoh moderatsiyasi
- [x] Ko'rishlar statistikasi
- [x] Qidiruv funksiyasi
- [x] Admin dashboard
- [x] Foydalanuvchilar ro'yxati

## ❌ Ishlamayotgan/Tugallanmagan Funksiyalar

- [ ] Settings saqlash
- [ ] Static pages CRUD
- [ ] Banner boshqaruvi
- [ ] Menu boshqaruvi
- [ ] Redirect boshqaruvi
- [ ] File upload optimizatsiya
- [ ] Email yuborish
- [ ] Redis caching
- [ ] Two-factor authentication

---

## 🔗 Keyingi Qadamlar

1. **Settings funksiyasini yakunlash**
   - Setting modelidan foydalanib saqlash
   - Settings service yaratish

2. **Static Pages CRUD**
   - StaticPage modeli tayyor
   - Admin UI tayyor
   - Faqat backend logic kerak

3. **Favicon qo'shish**
   - `/static/favicon.ico` yaratish

4. **Deprecation warninglarni tuzatish**
   - `regex` → `pattern`

---

*Bu hujjat Claude AI tomonidan 2026-01-29 sanasida yaratilgan.*
