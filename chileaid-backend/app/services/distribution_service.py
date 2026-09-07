"""Lógica de inventario/distribución de la organización (CU-08).

El **stock** por insumo es DERIVADO, no persistido (misma filosofía que
`cobertura`):

    disponible(insumo) = Σ need.cantidad_recibida − Σ DistributionLot.cantidad

Las entradas ya viven en `need.cantidad_recibida` (recepción, CU-07); un
`DistributionLot` registra una salida. `create_lot` valida `cantidad ≤ disponible`
recalculando el derivado bajo lock pesimista sobre las `needs` del insumo (mismo
patrón `SELECT ... FOR UPDATE` que `confirm_reception`), lo que serializa las
salidas concurrentes del mismo insumo y las recepciones en curso.
"""

from __future__ import annotations

import uuid
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import (
    DistributionLot,
    Insumo,
    LotSalida,
    Need,
    TipoCentro,
)
from app.schemas.distribution import CreateLotDTO, DistributionLotDTO, StockItemDTO
from app.services.org_service import get_center_by_organization

# Salidas permitidas por tipo de centro (gating del dominio, no del cliente).
_SALIDAS_POR_TIPO: dict[TipoCentro, tuple[LotSalida, ...]] = {
    TipoCentro.CENTRO_ACOPIO: (LotSalida.ENVIADO_A_TERRENO,),
    TipoCentro.PUNTO_DISTRIBUCION: (LotSalida.ENTREGADO_A_BENEFICIARIO,),
    TipoCentro.AMBOS: (LotSalida.ENVIADO_A_TERRENO, LotSalida.ENTREGADO_A_BENEFICIARIO),
}


def _build_lot_dto(lot: DistributionLot) -> DistributionLotDTO:
    """Construye el `DistributionLotDTO` (asume `lot.insumo` precargado)."""
    return DistributionLotDTO(
        id=str(lot.id),
        insumo_id=str(lot.insumo_id),
        insumo_nombre=lot.insumo.nombre,
        categoria=lot.insumo.categoria.value,
        unidad=lot.insumo.unidad,
        cantidad=lot.cantidad,
        tipo=lot.tipo.value,
        destino=lot.destino,
        fecha=lot.fecha.isoformat(),
    )


def _distribuido_por_insumo(db: Session, center_id: uuid.UUID) -> dict[uuid.UUID, int]:
    """Suma distribuida por insumo (Σ DistributionLot.cantidad) del centro."""
    rows = db.execute(
        select(DistributionLot.insumo_id, func.sum(DistributionLot.cantidad))
        .where(DistributionLot.center_id == center_id)
        .group_by(DistributionLot.insumo_id)
    ).all()
    return {insumo_id: int(total or 0) for insumo_id, total in rows}


def get_stock(db: Session, organization_id: uuid.UUID) -> list[StockItemDTO]:
    """Stock disponible por insumo del centro de la org (recibido − distribuido).

    Lista vacía si la org no tiene centro. Solo aparecen insumos que alguna vez se
    recibieron (`Σ recibida > 0`); `cantidadDisponible` puede ser 0 (todo distribuido).
    Ordenado por nombre de insumo.
    """
    center = get_center_by_organization(db, organization_id)
    if center is None:
        return []

    recibida_rows = db.execute(
        select(Need.insumo_id, func.sum(Need.cantidad_recibida))
        .where(Need.center_id == center.id)
        .group_by(Need.insumo_id)
    ).all()
    recibida = {insumo_id: int(total or 0) for insumo_id, total in recibida_rows}
    insumo_ids = [iid for iid, total in recibida.items() if total > 0]
    if not insumo_ids:
        return []

    distribuida = _distribuido_por_insumo(db, center.id)
    insumos = {
        i.id: i for i in db.scalars(select(Insumo).where(Insumo.id.in_(insumo_ids))).all()
    }

    items = [
        StockItemDTO(
            insumo_id=str(iid),
            insumo_nombre=insumos[iid].nombre,
            categoria=insumos[iid].categoria.value,
            unidad=insumos[iid].unidad,
            cantidad_disponible=recibida[iid] - distribuida.get(iid, 0),
        )
        for iid in insumo_ids
    ]
    items.sort(key=lambda s: s.insumo_nombre)
    return items


def get_lots(db: Session, organization_id: uuid.UUID) -> list[DistributionLotDTO]:
    """Lotes distribuidos del centro de la org, más recientes primero.

    Lista vacía si la org no tiene centro. Precarga el insumo para el DTO.
    """
    center = get_center_by_organization(db, organization_id)
    if center is None:
        return []

    lots = (
        db.scalars(
            select(DistributionLot)
            .where(DistributionLot.center_id == center.id)
            .order_by(DistributionLot.fecha.desc(), DistributionLot.created_at.desc())
            .options(joinedload(DistributionLot.insumo))
        )
        .unique()
        .all()
    )
    return [_build_lot_dto(lot) for lot in lots]


def create_lot(
    db: Session, organization_id: uuid.UUID, data: CreateLotDTO
) -> DistributionLotDTO:
    """Registra una salida de stock (CU-08).

    - 404 si la org no tiene centro o el insumo no existe.
    - 422 si el tipo de salida no corresponde al tipo de centro, o si la cantidad
      supera el stock disponible (recibido − distribuido).

    Serializa con recepciones/salidas concurrentes del mismo insumo releyendo sus
    `needs` con `FOR UPDATE` antes de recalcular el disponible.
    """
    center = get_center_by_organization(db, organization_id)
    if center is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La organización aún no tiene un centro registrado",
        )

    permitidas = _SALIDAS_POR_TIPO[center.organization.tipo_centro]
    if data.tipo not in permitidas:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El tipo de centro no permite esta salida de distribución",
        )

    insumo = db.get(Insumo, data.insumo_id)
    if insumo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El insumo no existe en el catálogo",
        )

    # Lock pesimista sobre las needs del insumo en el centro: serializa con la
    # recepción (que también lockea needs) y con otras salidas del mismo insumo.
    needs = (
        db.scalars(
            select(Need)
            .where(Need.center_id == center.id, Need.insumo_id == data.insumo_id)
            .with_for_update()
        )
        .all()
    )
    recibida = sum(n.cantidad_recibida for n in needs)
    distribuida = db.scalar(
        select(func.coalesce(func.sum(DistributionLot.cantidad), 0)).where(
            DistributionLot.center_id == center.id,
            DistributionLot.insumo_id == data.insumo_id,
        )
    )
    disponible = recibida - int(distribuida or 0)
    if data.cantidad > disponible:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Stock insuficiente (disponible {disponible})",
        )

    lot = DistributionLot(
        center_id=center.id,
        insumo_id=data.insumo_id,
        cantidad=data.cantidad,
        tipo=data.tipo,
        destino=data.destino,
        fecha=date.today(),
    )
    lot.insumo = insumo  # evita una query extra al construir el DTO
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return _build_lot_dto(lot)
