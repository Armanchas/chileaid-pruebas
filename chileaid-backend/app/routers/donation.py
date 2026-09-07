"""Router del aporte del donante (role=DONOR). CU-05."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import require_role
from app.models import User, UserRole
from app.schemas.donation import CreateDonationRequest, DonationDTO
from app.schemas.pagination import Page
from app.services.donation_service import (
    cancel_donation,
    create_donation,
    get_donations_for_donor,
)

router = APIRouter(prefix="/donations", tags=["donations"])


@router.get("", response_model=Page[DonationDTO])
def list_my_donations(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_role(UserRole.DONOR)),
    db: Session = Depends(get_db),
) -> Page[DonationDTO]:
    """Página de donaciones del donante autenticado (CU-06), más recientes primero.

    Filtra por el `donor_id` del JWT; cada ítem trae el insumo y su
    centro/organización resueltos. `items` vacío si el donante no tiene aportes.
    """
    items, total = get_donations_for_donor(db, current_user.id, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=DonationDTO, status_code=status.HTTP_201_CREATED)
def create_donation_endpoint(
    payload: CreateDonationRequest,
    current_user: User = Depends(require_role(UserRole.DONOR)),
    db: Session = Depends(get_db),
) -> DonationDTO:
    """Registra el aporte comprometido del donante autenticado (CU-05).

    201 con el `DonationDTO` (código de seguimiento + ítems). 404 si algún
    `needId` no existe; 422 si una necesidad no está activa o el aporte
    sobrepasaría su meta (RF-02/RF-04). El control de concurrencia vive en el
    service.
    """
    return create_donation(db, current_user.id, payload)


@router.post("/{donation_id}/cancel", response_model=DonationDTO)
def cancel_donation_endpoint(
    donation_id: uuid.UUID,
    current_user: User = Depends(require_role(UserRole.DONOR)),
    db: Session = Depends(get_db),
) -> DonationDTO:
    """Cancela (soft) el aporte pendiente del donante autenticado.

    200 con el `DonationDTO` en estado `cancelada`. 404 si la donación no existe
    o no le pertenece; 409 si ya fue recibida o cancelada. Revierte lo comprometido
    y reabre las necesidades cerradas al 100%; la lógica vive en el service.
    """
    return cancel_donation(db, current_user.id, donation_id)
