"""Lógica de negocio del aporte del donante (CU-05, RF-01/RF-02/RF-04).

`create_donation` registra una donación (header + items) en UNA transacción,
controlando el sobrestock de forma concurrente (RF-02):

- **Lock pesimista**: cada `Need` involucrada se relee con
  `SELECT ... FOR UPDATE` (`with_for_update`), que serializa los compromisos
  concurrentes en PostgreSQL.
- **Lock optimista de respaldo**: `Need.version_id` hace que un UPDATE perdido
  (típico en motores que ignoran `FOR UPDATE`, p. ej. SQLite) levante
  `StaleDataError`; aquí se reintenta sobre el estado fresco.
- **CheckConstraint** `ck_need_no_sobrestock`: última red de seguridad en la BD,
  no la validación primaria (esa es la comparación explícita de abajo, que da un
  422 legible indicando qué `needId` falló).

Al alcanzar la meta, la necesidad pasa a `COMPLETADA` (RF-04). El
`codigo_seguimiento` (RF-01) se genera con `secrets` (aleatoriedad
criptográfica) y se verifica único antes de persistir.
"""

from __future__ import annotations

import secrets
import uuid
from collections import OrderedDict

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.orm.exc import StaleDataError

from app.models import (
    Center,
    Donation,
    DonationItem,
    DonationStatus,
    MotivoCancelacion,
    Need,
    NeedStatus,
)
from app.schemas.donation import (
    CreateDonationRequest,
    DonationDTO,
    DonationItemDTO,
)

_CODE_PREFIX = "CA-"
_MAX_CODE_ATTEMPTS = 10
# Reintentos del compromiso completo ante colisión de bloqueo optimista (RF-02).
_MAX_CONCURRENCY_RETRIES = 50


def _generate_code() -> str:
    """`CA-` + 8 hex en mayúsculas, con aleatoriedad criptográfica (`secrets`)."""
    return _CODE_PREFIX + secrets.token_hex(4).upper()


def _generate_unique_code(db: Session) -> str:
    """Código de seguimiento único; reintenta si (improbable) colisiona."""
    for _ in range(_MAX_CODE_ATTEMPTS):
        codigo = _generate_code()
        existe = db.scalar(
            select(Donation.id).where(Donation.codigo_seguimiento == codigo)
        )
        if existe is None:
            return codigo
    raise RuntimeError("No se pudo generar un código de seguimiento único")


def build_donation_dto(donation: Donation) -> DonationDTO:
    """Construye el DonationDTO a partir del modelo persistido.

    Cada ítem resuelve su insumo y el centro/organización vía
    `need → insumo` y `need → center → organization`. Para listados, precargar
    esas relaciones (ver `get_donations_for_donor`) evita el N+1.
    """
    return DonationDTO(
        id=str(donation.id),
        codigo_seguimiento=donation.codigo_seguimiento,
        estado=donation.estado.value,
        items=[
            DonationItemDTO(
                need_id=str(it.need_id),
                cantidad=it.cantidad,
                insumo_nombre=it.need.insumo.nombre,
                insumo_unidad=it.need.insumo.unidad,
                centro_nombre=it.need.center.nombre,
                organizacion_nombre=it.need.center.organization.nombre,
                activo=it.activo,
                motivo_cancelacion=(
                    it.motivo_cancelacion.value if it.motivo_cancelacion else None
                ),
            )
            for it in donation.items
        ],
        created_at=donation.created_at.isoformat(),
        confirmado_at=(
            donation.confirmado_at.isoformat() if donation.confirmado_at else None
        ),
    )


def get_donations_for_donor(
    db: Session, donor_id: uuid.UUID, limit: int = 20, offset: int = 0
) -> tuple[list[DonationDTO], int]:
    """Página de donaciones del donante (CU-06), más recientes primero, con
    ítems expandidos. Devuelve `(items, total)`.

    Precarga `items → need → insumo` y `items → need → center → organization`
    para construir los DTO sin N+1.
    """
    total = (
        db.scalar(
            select(func.count()).select_from(Donation).where(Donation.donor_id == donor_id)
        )
        or 0
    )

    donations = (
        db.scalars(
            select(Donation)
            .where(Donation.donor_id == donor_id)
            .order_by(Donation.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(
                selectinload(Donation.items)
                .joinedload(DonationItem.need)
                .joinedload(Need.insumo),
                selectinload(Donation.items)
                .joinedload(DonationItem.need)
                .joinedload(Need.center)
                .joinedload(Center.organization),
            )
        )
        .unique()
        .all()
    )
    return [build_donation_dto(d) for d in donations], total


def cancel_donation(
    db: Session, donor_id: uuid.UUID, donation_id: uuid.UUID
) -> DonationDTO:
    """Cancela (soft) el aporte PENDIENTE del donante (dueño del JWT).

    - 404 si la donación no existe o no pertenece al donante (no se revela la
      existencia de aportes ajenos).
    - 409 si está `recibido` (una entrega ya confirmada no se anula) o ya
      `cancelada`.

    En éxito, dentro de una transacción: marca cada ítem activo como cancelado
    (`activo=False`, `motivo=DONANTE`), revierte `cantidad_comprometida` de su
    necesidad (releída con `FOR UPDATE`, mismo patrón que `create_donation`) y
    reabre la need si estaba `COMPLETADA`. Como se cancelan TODOS los ítems, la
    donación pasa a `CANCELADA`.
    """
    donation = db.scalar(
        select(Donation)
        .where(Donation.id == donation_id)
        .options(selectinload(Donation.items))
        .with_for_update(of=Donation)
    )
    if donation is None or donation.donor_id != donor_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La donación no existe o no te pertenece",
        )
    if donation.estado == DonationStatus.RECIBIDO:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Una donación ya recibida no se puede cancelar",
        )
    if donation.estado == DonationStatus.CANCELADA:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La donación ya fue cancelada",
        )

    for item in donation.items:
        if not item.activo:
            continue
        # Lock pesimista por necesidad (mismo patrón que create_donation).
        need = db.scalar(select(Need).where(Need.id == item.need_id).with_for_update())
        need.cantidad_comprometida -= item.cantidad
        # Se liberó cupo: una need cerrada al 100% vuelve a estar activa.
        if need.estado == NeedStatus.COMPLETADA:
            need.estado = NeedStatus.ACTIVA
        item.activo = False
        item.motivo_cancelacion = MotivoCancelacion.DONANTE

    # Todos los ítems quedaron cancelados → la donación padre pasa a CANCELADA.
    donation.estado = DonationStatus.CANCELADA
    db.commit()
    db.refresh(donation)
    return build_donation_dto(donation)


def create_donation(
    db: Session, donor_id: uuid.UUID, data: CreateDonationRequest
) -> DonationDTO:
    """Registra el aporte del donante (CU-05). Ver docstring del módulo.

    404 si algún `needId` no existe; 422 si una necesidad no está activa o el
    aporte sobrepasaría su meta (con el `needId` culpable en el detalle).
    """
    # Sumar cantidades por necesidad: un cliente podría repetir el mismo needId,
    # y la validación de sobrestock debe verse sobre el total, no línea a línea.
    requested: "OrderedDict[uuid.UUID, int]" = OrderedDict()
    for item in data.items:
        requested[item.need_id] = requested.get(item.need_id, 0) + item.cantidad

    for _ in range(_MAX_CONCURRENCY_RETRIES):
        try:
            return _commit_donation(db, donor_id, requested)
        except StaleDataError:
            # Un aporte concurrente tocó la necesidad entre el read y el commit;
            # el lock optimista lo detectó. Reintentar sobre el estado fresco.
            db.rollback()
        except HTTPException:
            # Validación de negocio (404/422): dejar la sesión limpia y propagar.
            db.rollback()
            raise

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="No se pudo registrar el aporte por alta concurrencia; reintenta",
    )


def _commit_donation(
    db: Session,
    donor_id: uuid.UUID,
    requested: "OrderedDict[uuid.UUID, int]",
) -> DonationDTO:
    """Un intento del compromiso, dentro de una sola transacción."""
    locked: list[tuple[Need, int]] = []
    # CU-05: un aporte (un código de seguimiento) va a UN solo centro. El centro
    # del primer ítem fija la referencia; los demás deben coincidir. `center_id`
    # ya viene en memoria tras el `with_for_update()`, así que no hay query extra.
    reference_center_id: uuid.UUID | None = None
    for need_id, cantidad in requested.items():
        # Lock pesimista por necesidad (serializa en Postgres; en SQLite el lock
        # optimista version_id cubre la carrera).
        need = db.scalar(select(Need).where(Need.id == need_id).with_for_update())
        if need is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La necesidad {need_id} no existe",
            )
        # Validar la pertenencia a un único centro ANTES de sobrestock/estado:
        # un aporte multi-centro es inválido de raíz, sin importar las cantidades.
        if reference_center_id is None:
            reference_center_id = need.center_id
        elif need.center_id != reference_center_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Todos los items deben pertenecer al mismo centro",
                    "needId": str(need_id),
                    "centerIds": {
                        "esperado": str(reference_center_id),
                        "recibido": str(need.center_id),
                    },
                },
            )
        if need.estado != NeedStatus.ACTIVA:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"La necesidad {need_id} no está activa",
            )
        if need.cantidad_comprometida + cantidad > need.cantidad_requerida:
            disponible = need.cantidad_requerida - need.cantidad_comprometida
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"El aporte excede lo disponible para la necesidad {need_id} "
                    f"(disponible {disponible}, solicitado {cantidad})"
                ),
            )

        need.cantidad_comprometida += cantidad
        # RF-04: cierre automático al alcanzar la meta.
        if need.cantidad_comprometida == need.cantidad_requerida:
            need.estado = NeedStatus.COMPLETADA
        locked.append((need, cantidad))

    donation = Donation(
        donor_id=donor_id,
        codigo_seguimiento=_generate_unique_code(db),
        estado=DonationStatus.PENDIENTE,
    )
    donation.items = [
        DonationItem(need_id=need.id, cantidad=cantidad) for need, cantidad in locked
    ]
    db.add(donation)
    db.commit()
    db.refresh(donation)
    return build_donation_dto(donation)
