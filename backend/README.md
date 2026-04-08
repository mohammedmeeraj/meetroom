
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
| Auth | JWT via [python-jose](https://github.com/mpdavis/python-jose) + bcrypt |
| Validation | Pydantic v2 + pydantic-settings |
