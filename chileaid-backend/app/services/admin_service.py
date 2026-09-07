"""Lógica de negocio del panel del administrador.

Gestiona las transiciones de estado de las organizaciones receptoras (CU-02):
PENDIENTE → ACTIVA (aprobación) o RECHAZADA (rechazo), ACTIVA → INACTIVA
(desactivación) e INACTIVA → ACTIVA (reactivación); y la gestión del catálogo
maestro de insumos (§1.2): alta (con reactivación de soft-deleted) y baja
lógica. El router decide los códigos de error HTTP; las reglas de negocio se
hacen valer aquí.
"""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import (
    ActivityType,
    Center,
    Emergency,
    EmergencyStatus,
    Insumo,
    Need,
    NeedStatus,
    Organization,
    OrganizationStatus,
)
from app.schemas.admin import AdminOrgDTO, CatalogActionResult, CreateInsumoDTO
from app.schemas.center import CreateEmergencyDTO, EmergencyDTO
from app.schemas.org import InsumoCatalogDTO
from app.services.activity_service import record_activity
from app.services.center_service import build_emergency_dto


def _build_dto(org: Organization) -> AdminOrgDTO:
    documentacion = org.documents[0].nombre_archivo if org.documents else ""
    return AdminOrgDTO(
        id=str(org.id),
        nombre=org.nombre,
        tipo=org.tipo_centro.value,
        rut=org.rut,
        contacto_nombre=org.contacto_nombre,
        email=org.user.email,
        telefono=org.telefono,
        region=org.region,
        documentacion=documentacion,
        estado=org.estado.value,
        fecha_registro=org.created_at.date().isoformat(),
        motivo_rechazo=org.motivo_rechazo,
    )


def _load_org(db: Session, org_id: uuid.UUID) -> Organization:
    org = db.scalar(
        select(Organization)
        .where(Organization.id == org_id)
        .options(joinedload(Organization.user), selectinload(Organization.documents))
    )
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organización no encontrada",
        )
    return org


def list_orgs(
    db: Session, estado: str | None = None, limit: int = 20, offset: int = 0
) -> tuple[list[AdminOrgDTO], int]:
    """Página de organizaciones, opcionalmente filtradas por estado.

    Devuelve `(items, total)`: `total` es el conteo de la query filtrada
    (sin `limit`/`offset`), para que el cliente calcule el número de páginas.
    """
    filters = []
    if estado:
        try:
            filters.append(Organization.estado == OrganizationStatus(estado))
        except ValueError:
            pass  # valor desconocido → sin filtro (devuelve todas)

    total = db.scalar(select(func.count()).select_from(Organization).where(*filters)) or 0

    q = (
        select(Organization)
        .where(*filters)
        .options(joinedload(Organization.user), selectinload(Organization.documents))
        .order_by(Organization.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    orgs = db.scalars(q).all()
    return [_build_dto(org) for org in orgs], total


def count_orgs_by_estado(db: Session) -> dict[str, int]:
    """Conteo de organizaciones por estado (para las pestañas del panel admin),
    independiente de la paginación/filtro de `list_orgs`."""
    rows = db.execute(
        select(Organization.estado, func.count()).group_by(Organization.estado)
    ).all()
    counts = {estado.value: 0 for estado in OrganizationStatus}
    for estado, count in rows:
        counts[estado.value] = count
    counts["todas"] = sum(counts.values())
    return counts


def approve_org(db: Session, org_id: uuid.UUID) -> None:
    """PENDIENTE → ACTIVA. 409 si la org no está pendiente."""
    org = _load_org(db, org_id)
    if org.estado != OrganizationStatus.PENDIENTE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se pueden aprobar organizaciones en estado pendiente",
        )
    org.estado = OrganizationStatus.ACTIVA
    record_activity(
        db, ActivityType.ORG_APROBADA, f"{org.nombre} fue aprobada", org.id
    )
    db.commit()


def reject_org(db: Session, org_id: uuid.UUID, motivo: str | None) -> None:
    """PENDIENTE → RECHAZADA. 409 si la org no está pendiente."""
    org = _load_org(db, org_id)
    if org.estado != OrganizationStatus.PENDIENTE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se pueden rechazar organizaciones en estado pendiente",
        )
    org.estado = OrganizationStatus.RECHAZADA
    org.motivo_rechazo = motivo
    record_activity(
        db, ActivityType.ORG_RECHAZADA, f"{org.nombre} fue rechazada", org.id
    )
    db.commit()


def deactivate_org(db: Session, org_id: uuid.UUID) -> None:
    """ACTIVA → INACTIVA. 409 si la org no está activa."""
    org = _load_org(db, org_id)
    if org.estado != OrganizationStatus.ACTIVA:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se pueden desactivar organizaciones activas",
        )
    org.estado = OrganizationStatus.INACTIVA
    db.commit()


def reactivate_org(db: Session, org_id: uuid.UUID) -> None:
    """INACTIVA → ACTIVA. 409 si la org no está inactiva."""
    org = _load_org(db, org_id)
    if org.estado != OrganizationStatus.INACTIVA:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se pueden reactivar organizaciones inactivas",
        )
    org.estado = OrganizationStatus.ACTIVA
    db.commit()


# ----------------------------------------------------------------------------
# Catálogo de insumos (§1.2)
# ----------------------------------------------------------------------------


def _build_insumo_dto(insumo: Insumo) -> InsumoCatalogDTO:
    return InsumoCatalogDTO(
        id=str(insumo.id),
        nombre=insumo.nombre,
        categoria=insumo.categoria.value,
        unidad=insumo.unidad,
        activo=insumo.activo,
    )


def create_insumo(db: Session, payload: CreateInsumoDTO) -> InsumoCatalogDTO:
    """Alta de un insumo en el catálogo maestro.

    La unicidad del nombre es case-insensitive (más estricta que el UNIQUE
    case-sensitive de la BD). Si ya existe un insumo ACTIVO con ese nombre → 409.
    Si existe pero está dado de baja (soft-deleted), se REACTIVA y actualiza en
    vez de insertar una fila nueva (insertar violaría el UNIQUE del nombre).
    """
    nombre = payload.nombre.strip()
    existing = db.scalar(
        select(Insumo).where(func.lower(Insumo.nombre) == nombre.lower())
    )

    if existing is not None:
        if existing.activo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un insumo con ese nombre en el catálogo",
            )
        # Existía soft-deleted: reactivar con los nuevos datos (mismo id).
        existing.nombre = nombre
        existing.categoria = payload.categoria
        existing.unidad = payload.unidad
        existing.activo = True
        db.commit()
        db.refresh(existing)
        return _build_insumo_dto(existing)

    insumo = Insumo(
        nombre=nombre,
        categoria=payload.categoria,
        unidad=payload.unidad,
        activo=True,
    )
    db.add(insumo)
    db.commit()
    db.refresh(insumo)
    return _build_insumo_dto(insumo)


def delete_insumo(db: Session, insumo_id: uuid.UUID) -> CatalogActionResult:
    """Baja lógica (soft-delete) de un insumo del catálogo.

    404 si no existe o ya estaba inactivo. 409 si alguna necesidad ACTIVA lo
    referencia (las cerradas/completadas NO bloquean: son historia). En éxito
    marca `activo=False` (la fila se conserva para preservar las needs históricas
    y el UNIQUE del nombre).
    """
    insumo = db.get(Insumo, insumo_id)
    if insumo is None or not insumo.activo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insumo no encontrado",
        )

    en_uso = db.scalar(
        select(Need)
        .where(Need.insumo_id == insumo_id, Need.estado == NeedStatus.ACTIVA)
        .limit(1)
    )
    if en_uso is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El insumo está en uso por una o más necesidades activas",
        )

    insumo.activo = False
    db.commit()
    return CatalogActionResult(success=True)


# ---------------------------------------------------------------------------
# Gestión de emergencias (admin) — el admin es dueño del catálogo de emergencias
# (crear/listar/cerrar). El vínculo centro↔emergencia lo hace la ORG desde su
# propio centro (ver org_service), no el admin.
# ---------------------------------------------------------------------------


def _emergencies_with_centers(db: Session, estado: EmergencyStatus | None):
    """Emergencias (opcionalmente filtradas por estado) con sus centros+needs
    precargados para derivar `cobertura`/`totalCentros` sin N+1."""
    query = (
        select(Emergency)
        .order_by(Emergency.fecha_inicio.desc())
        .options(selectinload(Emergency.centers).selectinload(Center.needs))
    )
    if estado is not None:
        query = query.where(Emergency.estado == estado)
    return db.scalars(query).unique().all()


def list_emergencies(db: Session, estado: str | None = None) -> list[EmergencyDTO]:
    """Emergencias para gestión del admin: activas Y cerradas (historial).

    A diferencia del `GET /emergencies` público (solo activas), este listado
    incluye todas. `estado` filtra opcionalmente (`activa`/`cerrada`); un valor
    inválido → 422.
    """
    estado_enum: EmergencyStatus | None = None
    if estado is not None:
        try:
            estado_enum = EmergencyStatus(estado)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Estado de emergencia inválido (usa 'activa' o 'cerrada')",
            )
    emergencias = _emergencies_with_centers(db, estado_enum)
    return [build_emergency_dto(e) for e in emergencias]


def create_emergency(db: Session, data: CreateEmergencyDTO) -> EmergencyDTO:
    """Crea una emergencia (nace `activa`, sin centros vinculados aún).

    Sin centros, `totalCentros=0` y `cobertura=0`. Las orgs vinculan sus centros
    después desde `/org/center`.
    """
    emergency = Emergency(
        nombre=data.nombre,
        tipo=data.tipo,
        zona=data.zona,
        fecha_inicio=data.fecha_inicio,
        estado=EmergencyStatus.ACTIVA,
    )
    db.add(emergency)
    db.commit()
    db.refresh(emergency)
    return build_emergency_dto(emergency)


def close_emergency(db: Session, emergency_id: uuid.UUID) -> EmergencyDTO:
    """Cierra una emergencia (`activa → cerrada`). Sin cascada.

    404 si no existe; 409 si ya está cerrada. NO limpia el `emergency_id` de los
    centros vinculados: se conserva como registro histórico ("este centro cubrió
    tal evento"). El `GET /emergencies` público deja de mostrarla al filtrar por
    activas.
    """
    emergency = db.get(Emergency, emergency_id)
    if emergency is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La emergencia no existe",
        )
    if emergency.estado == EmergencyStatus.CERRADA:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La emergencia ya está cerrada",
        )
    emergency.estado = EmergencyStatus.CERRADA
    db.commit()
    # Recarga con centros+needs para los agregados del DTO.
    emergency = db.scalar(
        select(Emergency)
        .where(Emergency.id == emergency_id)
        .options(selectinload(Emergency.centers).selectinload(Center.needs))
    )
    return build_emergency_dto(emergency)
