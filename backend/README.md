
# MeetRoom - Backend API

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=flat-square&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-1.18-orange?style=flat-square&logo=alembic&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

Anonymous video meeting backend. Handles host authentication, room lifecycle management, and LiveKit token issuance for guests. Built with FastAPI + SQLAlchemy.

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
|   |-- routers/
|   |-- schemas/
|   |-- core/
|   |   |-- config.py
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