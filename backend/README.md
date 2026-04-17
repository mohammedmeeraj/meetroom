
# MeetRoom - Backend API

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=flat-square&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-1.18-orange?style=flat-square&logo=alembic&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

MeetRoom backend. Handles host authentication, room lifecycle management, and LiveKit token issuance for guests. Built with FastAPI + SQLAlchemy.

---
## Table of contents
- [Stack](#stack)
- [Project structure](#project-structure)
- [Local development](#local-development)
- [Environment variables](#environment-variables)
- [API reference](#api-reference)
    - [Authentication](#authentication)
    - [Rooms](#rooms)
  

---
## Stack
| Layer | Technology |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com) 0.135 |
| ORM | [SQLAlchemy](https://www.sqlalchemy.org) 2.0 |
| Database | PostgreSQL (prod) / SQLite (dev) |
| Migrations | Alembic 1.18 |
| Auth | JWT via [python-jose](https://github.com/mpdavis/python-jose) + Argon2 |
| Validation | Pydantic v2 + pydantic-settings |

---
## Project Structure
```
backend/
|-- app/
|   |-- models/
|   |   |-- user.py                    # users table
|   |   |-- room.py                    # rooms table + slug generator
|   |-- routers/
|   |   |-- auth.py                    # POST /register  POST /login  GET /me
|   |   |-- rooms.py                   # CRUD for rooms + participant count
|   |-- schemas/
|   |   |-- auth.py                    # Pydantic models for auth endpoints
|   |   |-- room.py                    # Pydantic models for room
|   |-- core/
|   |   |-- config.py                  # Settings loaded from .env via pydantic
|   |   |-- security.py                # JWT, hashing, etc
|   |-- main.py                        # App factory, router registeration
|   |-- database.py                    # SQLAlchemy engine, SessionLocal, get_db() dependency
|   |-- dependencies.py                # get_settings() dependency
|-- alembic/
|-- alembic.ini
|-- requirements.txt
|-- .gitignore
|-- .env
|-- README.md 
```
---

## Local development

### Prerequisites

- Python 3.10+
- A [LiveKit Cloud](https://cloud.livekit.io) account (free tier) - or self-hosted LiveKit server

### Setup

```bash
# 1. Clone and enter the directory
cd backend

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate             #macOS / Linux: source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run alembic migrations
alembic upgrade head

# 5. Create your .env file and set the environment variables

# 6. Start the development server
uvicorn app.main:app --reload
```

The API is now running at **http://localhost:8000**

Interactive Swagger docs: **http://localhost:8000/docs**

ReDoc: **http://localhost:8000/redoc**

> SQLite is used by default in development - no database setup needed. The file 'meetroom.db' is created automatically when you run alembic migrations.

---

## Environment variables


| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | yes | `sqlite:///./meetroom.db` | SQLAlchemy connection string or PostgreSQL connection string|
| `SECRET_KEY` | yes | — | JWT signing key. Generate with `openssl rand -hex 32` |
| `ALGORITHM` | no | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | no | `10080` | Token TTL (default: 7 days) |
| `LIVEKIT_API_KEY` | yes | — | From your LiveKit project settings |
| `LIVEKIT_API_SECRET` | yes | — | From your LiveKit project settings |
| `LIVEKIT_URL` | yes | — | WebSocket URL, e.g. `wss://your-project.livekit.cloud` |
| `FRONTEND_URL` | yes | `http://localhost:5173` | Allowed CORS origin |
| `APP_NAME` | no | `MeetRoom` | Application name shown in docs |

### Example `.env`

```env
DATABASE_URL=postgresql://username:password@host:port/database_name
SECRET_KEY=your-generated-64-char-hex-secret
LIVEKIT_API_KEY=APIxxxxxxxxxxxxxxxx
LIVEKIT_API_SECRET=your_livekit_secret
LIVEKIT_URL=wss://your-project.livekit.cloud
FRONTEND_URL=https://your-frontend-url.com
```


## API reference

All endpoints are prefixed with '/api'. Authenticated endpoints require a `Bearer` token in the `Authorization` header.

### Authentication

#### `POST /api/auth/register`

Create a new user. Returns a JWT and the created user.

**No authentication required.**

**Request body**

```json
{
    "email": "you@example.com",
    "password": "yourpassword"
}
```

**Response `201`**

```json
{
    "access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZXhwIjoxNzc....",
    "token_type":"bearer",
    "user":{
        "id": 1,
        "email":"you@example.com",
        "is_active": true,
        "created_at": "2026-04-13T11:25:19"
    }
}
```

**Errors**

| Status | Detail |
|---|---|
| `400` | An account with this email already exists |

---

#### `POST /api/auth/login`

Authenticates an existing host. Returns a JWT

**No authentication required.**

**Request body**

```json
{
    "email": "you@example.com",
    "password": "yourpassword"
}
```

**Response `200`** - same response as `/register`

**Errors**

| Status | Detail |
|---|---|
| `401` | Incorrect email or password |
| `403` | Account is disabled |

---

#### `GET /api/auth/me`

Return the currently authenticated host.

**Requires authentication.**

**Response `200`**

```json
{
    "id": 1,
    "email": "you@example.com",
    "is_active": true,
    "created_at": "2026-04-13T07:14:34"
}
```
---