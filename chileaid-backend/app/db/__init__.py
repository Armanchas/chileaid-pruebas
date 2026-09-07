"""Capa de acceso a datos: engine, sesión y dependency de FastAPI."""

from .database import SessionLocal, engine, get_db

__all__ = ["engine", "SessionLocal", "get_db"]
