"""Primitivas de seguridad: verificación de passwords y JWT.

No contiene lógica HTTP ni acceso a BD; solo cripto pura, reutilizable por
routers y dependencies.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Mismo esquema (bcrypt) con que el seed hashea las passwords.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    """True si `plain` corresponde al hash bcrypt almacenado."""
    return pwd_context.verify(plain, hashed)


def hash_password(plain: str) -> str:
    """Devuelve el hash bcrypt de `plain`, listo para `users.password_hash`.

    Mismo esquema con que el seed hashea las passwords; nunca se persiste la
    contraseña en claro (CU-01).
    """
    return pwd_context.hash(plain)


def create_access_token(data: dict) -> str:
    """Firma un JWT con los claims de `data` + expiración (`exp`)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Devuelve los claims si el token es válido y no expiró; None si no."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
