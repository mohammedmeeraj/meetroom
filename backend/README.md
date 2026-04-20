
# MeetRoom - Backend API

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=flat-square&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-1.18-orange?style=flat-square&logo=alembic&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

MeetRoom backend. Handles host authentication, room lifecycle management, and LiveKit token issuance for guests. Built with FastAPI + SQLAlchemy.

---
## Table of contents
- [Features](#features)
- [Stack](#stack)
- [Project structure](#project-structure)
- [Local development](#local-development)
- [Environment variables](#environment-variables)
- [API reference](#api-reference)
    - [Authentication](#authentication)
    - [Rooms](#rooms)
- [Authentication model](#authentication-model)
  
---

##Features
### Host authentication

- Register and sign in with email and password
- Passwords hashed with Argon2 - plaintext never stored
- JWT-based sessions with configurable expiry (default 7 days)
- Protected routes via a `get_current_active_user()` FastAPI dependency

### Room management

- Hosts can create named meeting room - each generate a unique short slug (e.g. `drv-8f2a`)
- Shareable guest link derived from slug: `/m/{slug}`
- Rooms list per host, ordered newest first
- Public room lookup by slug - used by the guest join page to verify a room exists before asking for a display name
- Rooms have two states: **active** and **ended**
- Host can end a room via `PATCH /room/{slug}/end` - marks it inactive in the db and simultaneously kicks all connected participants

### Live participant counts
 
- `GET /rooms/{slug}/participants` queries LiveKit's server API in real time
- Returns participant count and display names for the dashboard
- Fails gracefully — returns `{ count: 0 }` if LiveKit is unreachable, never errors
- Safe to poll on a short interval

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

# 4. Create your .env file and set the environment variables

# 5. Run alembic migrations
alembic upgrade head

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
SECRET_KEY=your-generated-secret-key
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

### Rooms

#### `POST /api/rooms`

Create a new meeting room. Generates a unique slug used as the shareable room ID.

**Requires authentication.**

**Request body**

```json
{
  "name": "Design Review"
}
```
**Response `201`**

```json
{
  "id": 1,
  "slug": "drv-8f2a",
  "name": "Design Review",
  "is_active": true,
  "host_id": 1,
  "created_at": "2026-04-16T15:56:48",
  "ended_at": null
}
```

---

#### `GET /api/rooms`

List all rooms created by the authenticated host, newest first.

**Requires authentication.**

**Response `200`** — array of room objects (same shape as above)

---

#### `GET /api/rooms/{slug}`
 
Get a single room by slug. Used by the guest join page to verify the room exists before asking for a username.
 
**No authentication required.**
 
**Response `200`** — room object
 
**Errors**
 
| Status | Detail |
|---|---|
| `404` | Room not found |

---

#### `PATCH /api/rooms/{slug}/end`
 
Mark a room as ended and immediately kick all connected participants from LiveKit. Only the room's host can call this.
 
**Requires authentication.**
 
**Response `200`** — updated room object with `is_active: false` and `ended_at` set
 
**Errors**
 
| Status | Detail |
|---|---|
| `403` | Only the host can end this room |
| `404` | Room not found |
 
---

#### `GET /api/rooms/{slug}/participants`
 
Return the current live participant count for a room, fetched directly from LiveKit.
 
**No authentication required.**
 
**Response `200`**
 
```json
{
  "count": 4,
  "participants": ["Alex", "Jordan", "Sam", "Morgan"]
}
```
 
> Returns `{ "count": 0, "participants": [] }` if the room is inactive or LiveKit is unreachable — never errors. Safe to poll on a timer.
 
---

## Authentication model

Hosts authenticate with email and password. Guests do not authenticate at all.

**JWT flow**

1. Host calls `POST /api/auth/login` with credentials
2. Server returns a signed JWT (`HS256`, default TTL 7 days)
3. Frontend stores the token and attaches it to every subsequent request:
   ```
   Authorization: Bearer <token>
   ```
4. `get_current_active_user()` FastAPI dependency decodes and validates the token on every protected route