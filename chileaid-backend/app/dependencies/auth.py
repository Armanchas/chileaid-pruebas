"""Dependencies de FastAPI para autenticación y autorización por rol."""

from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db
from app.models import User, UserRole

# tokenUrl apunta al endpoint de login (para el flujo de Swagger).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resuelve el User autenticado a partir del JWT (claim `sub` = user.id).

    Lanza 401 si el token es inválido/expirado, no trae `sub` válido, o el
    usuario ya no existe.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    sub = payload.get("sub")
    if sub is None:
        raise credentials_exception

    # `sub` viaja como string; los PK son UUID.
    try:
        user_id = uuid.UUID(sub)
    except (ValueError, TypeError):
        raise credentials_exception

    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise credentials_exception
    return user


def require_role(*roles: UserRole):
    """Factory de dependency: exige que el usuario tenga uno de los `roles`.

    Uso:  Depends(require_role(UserRole.ADMIN))
          Depends(require_role(UserRole.ORG, UserRole.ADMIN))
    Lanza 403 si el rol no está permitido.
    """

    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción",
            )
        return current_user

    return checker


def get_current_organization_id(
    current_user: User = Depends(require_role(UserRole.ORG)),
    token: str = Depends(oauth2_scheme),
) -> uuid.UUID:
    """Resuelve el `organization_id` de la org autenticada desde el JWT.

    Exige `role=ORG` (403 vía `require_role`) y lee el claim `organization_id`
    que el login incrusta en el token. 403 si el token no trae una organización
    válida (p. ej. una cuenta org sin organización asociada).
    """
    payload = decode_access_token(token)
    org_id_raw = payload.get("organization_id") if payload else None
    if org_id_raw is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El token no tiene una organización asociada",
        )
    try:
        return uuid.UUID(org_id_raw)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El token no tiene una organización válida",
        )
