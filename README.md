# 🚀 Modern CMS

A modern, fast, and secure content management system built with Python and FastAPI.

## ✨ Features

- 🔐 **JWT Authentication** - Secure login with access & refresh tokens
- 👥 **User Management** - Groups, permissions, banning
- 📝 **Posts/Articles** - Categories, tags, SEO optimization
- 💬 **Comments** - Nested replies, voting, moderation
- 📊 **Analytics** - View tracking, rating system
- 🖼️ **Media** - Image optimization, thumbnails
- ⚡ **High Performance** - Async operations, caching ready
- 📱 **API-First** - RESTful API with OpenAPI docs

## 📋 Requirements

- Python 3.10+
- SQLite (default) or PostgreSQL
- Redis (optional, for caching)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd dle_python

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 3. Run Development Server

```bash
# Option 1: Using script
chmod +x run_dev.sh
./run_dev.sh

# Option 2: Manual
uvicorn app.main:app --reload
```

### 4. Access the API

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
dle_python/
├── app/
│   ├── api/                 # API endpoints
│   │   ├── deps.py          # Dependencies (auth, etc.)
│   │   └── v1/              # API version 1
│   │       ├── auth.py      # Authentication
│   │       ├── users.py     # User management
│   │       ├── posts.py     # Posts/Articles
│   │       ├── categories.py # Categories & Tags
│   │       └── comments.py  # Comments
│   ├── core/                # Core functionality
│   │   ├── config.py        # Settings
│   │   ├── database.py      # Database connection
│   │   └── security.py      # JWT & Password hashing
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py          # User, UserGroup
│   │   ├── post.py          # Post, Tag
│   │   ├── category.py      # Category
│   │   ├── comment.py       # Comment
│   │   └── cms.py           # StaticPage, Banner, etc.
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── utils/               # Utility functions
│   └── main.py              # FastAPI application
├── static/                  # Static files
├── uploads/                 # User uploads
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── run_dev.sh              # Development script
```

## 🔑 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Logout |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Get current user |
| PATCH | `/api/v1/users/me` | Update profile |
| POST | `/api/v1/users/me/password` | Change password |
| GET | `/api/v1/users/{id}` | Get user by ID |
| GET | `/api/v1/users` | List users (admin) |

### Posts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/posts` | List posts |
| GET | `/api/v1/posts/featured` | Featured posts |
| GET | `/api/v1/posts/popular` | Popular posts |
| GET | `/api/v1/posts/{id}` | Get post |
| POST | `/api/v1/posts` | Create post |
| PATCH | `/api/v1/posts/{id}` | Update post |
| DELETE | `/api/v1/posts/{id}` | Delete post |
| POST | `/api/v1/posts/{id}/rate` | Rate post |

### Categories & Tags
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/categories` | List categories |
| GET | `/api/v1/categories/tree` | Category tree |
| GET | `/api/v1/tags` | List tags |
| GET | `/api/v1/tags/popular` | Popular tags |

### Comments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/comments/post/{id}` | Get comments for post |
| POST | `/api/v1/comments` | Create comment |
| PATCH | `/api/v1/comments/{id}` | Update comment |
| DELETE | `/api/v1/comments/{id}` | Delete comment |
| POST | `/api/v1/comments/{id}/vote` | Vote on comment |

## 🔐 Default User Groups

| ID | Name | Description |
|----|------|-------------|
| 1 | Administrator | Full access |
| 2 | User | Basic user, can comment |
| 3 | Editor | Can create/edit posts |
| 4 | Moderator | Can moderate content |

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | Modern CMS |
| `DEBUG` | Debug mode | false |
| `SECRET_KEY` | App secret key | *required* |
| `DATABASE_URL` | Database connection | sqlite |
| `JWT_SECRET_KEY` | JWT signing key | *required* |
| `REDIS_URL` | Redis URL (optional) | - |
| `SMTP_HOST` | Email server | localhost |

## 🚀 Deployment

### Using Docker (Coming Soon)

```bash
docker-compose up -d
```

### Using PM2

```bash
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name cms
```

### Using Gunicorn

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📝 Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Formatting

```bash
black app/
isort app/
```

## 📄 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

Built with ❤️ using FastAPI, SQLAlchemy, and Python
