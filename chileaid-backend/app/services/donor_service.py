"""Lógica de negocio del perfil del donante particular (AC-01).

Gemelo simplificado de las funciones de perfil de `org_service.py`: el donante no
tiene una entidad institucional separada, sus datos viven directo en `User`. El
único caso de negocio es la unicidad del email (409 si lo toma otra cuenta).
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.user import DonorProfileDTO, UpdateDonorProfileDTO


def build_donor_profile_dto(user: User) -> DonorProfileDTO:
    """Construye el DonorProfileDTO a partir del User autenticado.

    `fechaRegistro` = `created_at` truncado a fecha ISO (YYYY-MM-DD).
    """
    return DonorProfileDTO(
        nombre=user.nombre,
        apellido=user.apellido,
        email=user.email,
        fecha_registro=user.created_at.date().isoformat(),
    )


def update_donor_profile(
    db: Session, current_user: User, payload: UpdateDonorProfileDTO
) -> DonorProfileDTO:
    """Actualiza los datos personales del donante autenticado.

    `nombre`/`apellido` van directo al User. Si el `email` cambia, se verifica
    que no esté tomado por OTRA cuenta (409) antes de actualizarlo.
    """
    current_user.nombre = payload.nombre
    current_user.apellido = payload.apellido

    if payload.email != current_user.email:
        taken = db.scalar(
            select(User).where(
                User.email == payload.email,
                User.id != current_user.id,
            )
        )
        if taken is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya está en uso por otra cuenta",
            )
        current_user.email = payload.email

    db.commit()
    db.refresh(current_user)
    return build_donor_profile_dto(current_user)
