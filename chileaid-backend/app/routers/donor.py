"""Router del perfil del donante particular (role=DONOR).

El donante se resuelve del JWT (claim `sub`); `require_role` entrega el `User`
autenticado. Gemelo simplificado de `GET/PUT /org/profile`.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import require_role
from app.models import User, UserRole
from app.schemas.user import DonorProfileDTO, UpdateDonorProfileDTO
from app.services.donor_service import build_donor_profile_dto, update_donor_profile

router = APIRouter(prefix="/me/donor", tags=["donor"])


@router.get("", response_model=DonorProfileDTO)
def get_my_profile(
    current_user: User = Depends(require_role(UserRole.DONOR)),
) -> DonorProfileDTO:
    """Perfil del donante autenticado (datos personales + fecha de registro)."""
    return build_donor_profile_dto(current_user)


@router.put("", response_model=DonorProfileDTO)
def update_my_profile(
    payload: UpdateDonorProfileDTO,
    current_user: User = Depends(require_role(UserRole.DONOR)),
    db: Session = Depends(get_db),
) -> DonorProfileDTO:
    """Actualiza nombre/apellido/email del donante autenticado.

    422 si la validación de Pydantic falla (campos vacíos / email inválido);
    409 si el nuevo email ya está tomado por otra cuenta (lo hace valer el service).
    """
    return update_donor_profile(db, current_user, payload)
