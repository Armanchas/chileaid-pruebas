"""Lógica de la recepción de donaciones por la organización (CU-07).

La org confirma físicamente una donación comprometida (por su `codigo_seguimiento`,
RF-01): la donación pasa de `pendiente` a `recibido`, se sella `confirmado_at` y
cada necesidad involucrada incrementa su `cantidad_recibida`.

Aislamiento por organización: una org solo ve y confirma donaciones cuyos ítems
pertenecen a necesidades de SU centro. Gracias al guard "1 donación = 1 centro"
(POST /donations), todos los ítems de una donación comparten centro, así que basta
mirar el centro del primer ítem para resolver la pertenencia.

El incremento usa el MISMO patrón de bloqueo que `POST /donations`: cada `Need` se
relee con `SELECT ... FOR UPDATE` y la donación se bloquea para serializar dos
confirmaciones concurrentes del mismo código.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import Donation, DonationItem, DonationStatus, Need
from app.schemas.reception import (
    ConfirmReceptionResult,
    PendingReceptionDTO,
    ReceptionItemDTO,
)
from app.services.org_service import get_center_by_organization


def _build_pending_dto(donation: Donation) -> PendingReceptionDTO:
    """Construye el `PendingReceptionDTO` de una donación pendiente.

    Omite los ítems cancelados (`activo=False`): la org no debe recibir un aporte
    que el donante anuló o que quedó sin destino al cerrarse su necesidad.
    """
    return PendingReceptionDTO(
        donation_id=str(donation.id),
        codigo_seguimiento=donation.codigo_seguimiento,
        items=[
            ReceptionItemDTO(
                need_id=str(it.need_id),
                insumo_nombre=it.need.insumo.nombre,
                cantidad=it.cantidad,
            )
            for it in donation.items
            if it.activo
        ],
        created_at=donation.created_at.isoformat(),
    )


def list_pending_receptions(
    db: Session, organization_id: uuid.UUID
) -> list[PendingReceptionDTO]:
    """Donaciones `pendiente` del centro de la org autenticada (CU-07).

    Lista vacía si la org no tiene centro o no tiene donaciones pendientes. Solo
    se devuelven donaciones cuyos ítems pertenecen a necesidades de SU centro.
    """
    center = get_center_by_organization(db, organization_id)
    if center is None:
        return []

    donations = (
        db.scalars(
            select(Donation)
            .join(Donation.items)
            .join(DonationItem.need)
            .where(
                Need.center_id == center.id,
                Donation.estado == DonationStatus.PENDIENTE,
            )
            .order_by(Donation.created_at.desc())
            .options(
                selectinload(Donation.items)
                .joinedload(DonationItem.need)
                .joinedload(Need.insumo)
            )
        )
        .unique()
        .all()
    )
    return [_build_pending_dto(d) for d in donations]


def confirm_reception(
    db: Session, organization_id: uuid.UUID, codigo: str
) -> ConfirmReceptionResult:
    """Confirma la recepción de una donación por su código (CU-07).

    - 404 si el código no existe.
    - 403 si la donación no pertenece al centro de la org autenticada.
    - 409 si la donación ya está `recibido`.

    En éxito, dentro de una transacción: marca `recibido`, sella `confirmado_at` e
    incrementa `cantidad_recibida` de cada necesidad (releída con `FOR UPDATE`).
    """
    donation = db.scalar(
        select(Donation)
        .where(Donation.codigo_seguimiento == codigo)
        .options(
            selectinload(Donation.items).joinedload(DonationItem.need)
        )
        .with_for_update(of=Donation)
    )
    if donation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe una donación con ese código",
        )

    # Pertenencia: el centro del primer ítem (Task A garantiza centro único).
    donation_center_id = donation.items[0].need.center_id
    center = get_center_by_organization(db, organization_id)
    if center is None or donation_center_id != center.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La donación no pertenece a tu centro",
        )

    if donation.estado == DonationStatus.RECIBIDO:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La donación ya fue confirmada como recibida",
        )

    for item in donation.items:
        # Los ítems cancelados (donante o cierre de need) no se reciben.
        if not item.activo:
            continue
        # Lock pesimista por necesidad (mismo patrón que POST /donations).
        need = db.scalar(
            select(Need).where(Need.id == item.need_id).with_for_update()
        )
        need.cantidad_recibida += item.cantidad

    donation.estado = DonationStatus.RECIBIDO
    donation.confirmado_at = datetime.now(timezone.utc)
    db.commit()

    return ConfirmReceptionResult(
        success=True,
        codigo_seguimiento=donation.codigo_seguimiento,
        estado=donation.estado.value,
    )
