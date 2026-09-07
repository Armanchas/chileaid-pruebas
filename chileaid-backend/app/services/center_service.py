"""Lógica de lectura de centros para el donante/público (CU-04, CU-10/CU-11).

A diferencia de `org_service` (panel de la organización, role=org), estas
lecturas son accesibles sin rol de organización: alimentan el listado/mapa, la
vista de detalle del centro y el flujo de donación del donante. Reutiliza
`build_need_dto`, `_cobertura` y `_center_estado` de `org_service` para no
duplicar la forma del `NeedDTO` unificado ni la derivación de cobertura/estado.

`region` se DERIVA de la organización dueña (el modelo `Center` no tiene columna
`region`; `zona` es la comuna). `cobertura`/`estado` de saturación se derivan
agregando las necesidades del centro.
"""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import Center, Emergency, EmergencyStatus, Need, NeedStatus, Urgencia
from app.schemas.center import CenterDetailDTO, CenterDTO, EmergencyDTO
from app.schemas.org import NeedDTO
from app.services.org_service import _cobertura, _center_estado, build_need_dto

# Orden de prioridad para listar las necesidades "urgentes" (chips de la tarjeta).
_URGENCIA_RANK = {Urgencia.ALTA: 0, Urgencia.MEDIA: 1, Urgencia.BAJA: 2}


def list_active_needs_for_center(
    db: Session, center_id: uuid.UUID
) -> list[NeedDTO]:
    """Necesidades ACTIVAS de un centro (las únicas donables), CU-04.

    404 si el centro no existe; lista vacía si existe pero no tiene necesidades
    activas. Solo se exponen las `ACTIVA`: las completadas/cerradas no reciben
    nuevos aportes.
    """
    center = db.get(Center, center_id)
    if center is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El centro no existe",
        )

    needs = db.scalars(
        select(Need)
        .where(Need.center_id == center_id, Need.estado == NeedStatus.ACTIVA)
        .order_by(Need.created_at)
        .options(joinedload(Need.insumo))
    ).all()
    return [build_need_dto(n) for n in needs]


# ----------------------------------------------------------------------------
# Listado / mapa de centros y emergencias (CU-10/CU-11)
# ----------------------------------------------------------------------------


def _center_cobertura_general(center: Center) -> int:
    """Cobertura agregada (0-100) del centro a partir de todas sus necesidades."""
    requerida = sum(n.cantidad_requerida for n in center.needs)
    comprometida = sum(n.cantidad_comprometida for n in center.needs)
    return _cobertura(comprometida, requerida)


def _necesidades_urgentes(center: Center) -> list[str]:
    """Nombres de los insumos de las necesidades ACTIVAS, urgentes primero."""
    activas = [n for n in center.needs if n.estado == NeedStatus.ACTIVA]
    activas.sort(key=lambda n: _URGENCIA_RANK.get(n.urgencia, 9))
    return [n.insumo.nombre for n in activas]


def build_center_dto(center: Center) -> CenterDTO:
    """Construye el `CenterDTO` del listado, con cobertura/estado derivados.

    Asume `center.organization`, `center.emergency` y `center.needs` (con su
    insumo) precargados para no disparar queries N+1.
    """
    cobertura = _center_cobertura_general(center)
    org = center.organization
    return CenterDTO(
        id=str(center.id),
        nombre=center.nombre,
        organizacion=org.nombre,
        zona=center.zona,
        region=org.region,
        cobertura=cobertura,
        estado=_center_estado(center, cobertura),
        emergencia_id=str(center.emergency_id) if center.emergency_id else None,
        tipo_emergencia=center.emergency.tipo.value if center.emergency else None,
        emergencia_nombre=center.emergency.nombre if center.emergency else None,
        tipo_centro=org.tipo_centro.value,
        necesidades_urgentes=_necesidades_urgentes(center),
        direccion=center.direccion,
        latitud=float(center.latitud) if center.latitud is not None else None,
        longitud=float(center.longitud) if center.longitud is not None else None,
    )


def build_emergency_dto(emergency: Emergency) -> EmergencyDTO:
    """Construye el `EmergencyDTO` con agregados de sus centros (promedio cobertura).

    Asume `emergency.centers` (con sus `needs`) precargados.
    """
    centros = emergency.centers
    total = len(centros)
    cobertura = (
        round(sum(_center_cobertura_general(c) for c in centros) / total)
        if total
        else 0
    )
    return EmergencyDTO(
        id=str(emergency.id),
        nombre=emergency.nombre,
        tipo=emergency.tipo.value,
        zona=emergency.zona,
        fecha_inicio=emergency.fecha_inicio.isoformat(),
        estado=emergency.estado.value,
        total_centros=total,
        cobertura=cobertura,
    )


def list_active_emergencies(db: Session) -> list[EmergencyDTO]:
    """Emergencias activas con sus agregados (CU para `getActiveEmergencies`)."""
    emergencies = (
        db.scalars(
            select(Emergency)
            .where(Emergency.estado == EmergencyStatus.ACTIVA)
            .order_by(Emergency.fecha_inicio.desc())
            .options(selectinload(Emergency.centers).selectinload(Center.needs))
        )
        .unique()
        .all()
    )
    return [build_emergency_dto(e) for e in emergencies]


def list_centers(
    db: Session,
    *,
    region: str | None = None,
    tipo: str | None = None,
    estado: str | None = None,
    emergencia_id: str | None = None,
    orden: str | None = None,
) -> list[CenterDTO]:
    """Lista pública de centros con filtros opcionales (CU-10/CU-11).

    `region`/`tipo`/`emergenciaId` filtran por org/emergencia; `estado` filtra por
    la saturación DERIVADA (`critico`/`en_capacidad`/`cerrado`), por eso se aplica
    en memoria tras construir los DTO. `orden=cobertura_asc` ordena ascendente por
    cobertura (caso "centros críticos primero").
    """
    centers = (
        db.scalars(
            select(Center)
            .order_by(Center.created_at)
            .options(
                joinedload(Center.organization),
                joinedload(Center.emergency),
                selectinload(Center.needs).joinedload(Need.insumo),
            )
        )
        .unique()
        .all()
    )
    dtos = [build_center_dto(c) for c in centers]

    if region:
        dtos = [d for d in dtos if d.region == region]
    if tipo:
        dtos = [d for d in dtos if d.tipo_centro == tipo]
    if emergencia_id:
        dtos = [d for d in dtos if d.emergencia_id == emergencia_id]
    if estado:
        dtos = [d for d in dtos if d.estado == estado]

    if orden == "cobertura_asc":
        dtos.sort(key=lambda d: d.cobertura)
    return dtos


def get_center_detail(db: Session, center_id: uuid.UUID) -> CenterDetailDTO:
    """Detalle de un centro (CU-04/CU-11). 404 si el centro no existe.

    Incluye datos operativos de la org dueña, la emergencia asociada (o `null`) y
    TODAS las necesidades del centro (no solo las activas: la vista segmenta
    urgentes/otras/completadas).
    """
    center = db.scalar(
        select(Center)
        .where(Center.id == center_id)
        .options(
            joinedload(Center.organization),
            joinedload(Center.emergency),
            selectinload(Center.needs).joinedload(Need.insumo),
        )
    )
    if center is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El centro no existe",
        )

    base = build_center_dto(center)
    org = center.organization
    emergencia = _emergency_dto_for_center(db, center)
    return CenterDetailDTO(
        **base.model_dump(by_alias=False),
        horario=center.horario_atencion,
        coordinador=org.contacto_nombre,
        telefono=org.telefono,
        emergencia=emergencia,
        necesidades=[build_need_dto(n) for n in center.needs],
    )


def _emergency_dto_for_center(db: Session, center: Center) -> EmergencyDTO | None:
    """`EmergencyDTO` de la emergencia del centro (con agregados), o None.

    Recarga la emergencia con TODOS sus centros+needs para calcular el promedio de
    cobertura (el `joinedload(Center.emergency)` del detalle no trae los otros
    centros de la emergencia).
    """
    if center.emergency_id is None:
        return None
    emergency = db.scalar(
        select(Emergency)
        .where(Emergency.id == center.emergency_id)
        .options(selectinload(Emergency.centers).selectinload(Center.needs))
    )
    return build_emergency_dto(emergency) if emergency else None
