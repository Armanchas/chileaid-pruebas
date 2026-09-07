"""Router de autenticación: login (CU-09) y registro de organización (CU-01)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.limiter import limiter
from app.core.security import create_access_token, verify_password
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models import Organization, User, UserRole
from app.schemas.auth import (
    LoginRequest,
    MeDTO,
    OrgRegisterRequest,
    RegisterDonorRequest,
    RegisterResult,
    TokenResponse,
)
from app.services.org_service import register_donor, register_organization

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(
    request: Request, credentials: LoginRequest, db: Session = Depends(get_db)
) -> TokenResponse:
    """Verifica credenciales y emite un JWT.

    Payload del token: `sub` (user.id como string), `role` y, solo para orgs,
    `organization_id`. 401 si el email no existe o la password no coincide.

    Limitado a 5 intentos/minuto por IP (§2.3): protege contra fuerza bruta y
    enumeración de emails sin cambiar el mensaje de error genérico.
    """
    user = db.scalar(select(User).where(User.email == credentials.email))
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload: dict = {"sub": str(user.id), "role": user.role.value}

    # Si es organización, incrustar su organization_id para que los endpoints
    # de org resuelvan el contexto del token sin otra consulta.
    if user.role == UserRole.ORG:
        org = db.scalar(select(Organization).where(Organization.user_id == user.id))
        if org is not None:
            payload["organization_id"] = str(org.id)

    return TokenResponse(access_token=create_access_token(payload))


@router.post(
    "/register/donor",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_donor_endpoint(
    payload: RegisterDonorRequest, db: Session = Depends(get_db)
) -> TokenResponse:
    """Registra un donante particular e inicia sesión de inmediato."""
    access_token = register_donor(db, payload)
    return TokenResponse(access_token=access_token)


@router.post(
    "/register/org",
    response_model=RegisterResult,
    status_code=status.HTTP_201_CREATED,
)
def register_org(
    payload: OrgRegisterRequest, db: Session = Depends(get_db)
) -> RegisterResult:
    """Registra una organización receptora (CU-01).

    Crea la cuenta-representante (role=org) y la organización en estado
    PENDIENTE. 201 en éxito, con un JWT (igual al de /auth/login) para que el
    frontend suba el documento de respaldo en el mismo flujo de registro; la
    org sigue Pendiente de aprobación del admin pese a recibir token. 409 si
    el email ya está registrado; 422 por validación (campos vacíos, región
    fuera de catálogo, passwords que no coinciden).
    """
    access_token = register_organization(db, payload)
    return RegisterResult(success=True, token=access_token)


@router.get("/me", response_model=MeDTO)
def get_me(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> MeDTO:
    """Valida el token server-side y devuelve la identidad autenticada (§1.7).

    A diferencia de `utils/jwt.ts` en el frontend (que decodifica el payload
    del JWT sin verificar la firma, §2.2), este endpoint sí valida firma y
    expiración vía `get_current_user`; 401 si el token es inválido/expiró o el
    usuario ya no existe. `organization_id` se resuelve fresco desde la BD
    (no del claim del token) para orgs.
    """
    organization_id: str | None = None
    if current_user.role == UserRole.ORG:
        org = db.scalar(
            select(Organization).where(Organization.user_id == current_user.id)
        )
        if org is not None:
            organization_id = str(org.id)

    return MeDTO(
        id=str(current_user.id),
        role=current_user.role.value,
        organization_id=organization_id,
    )
