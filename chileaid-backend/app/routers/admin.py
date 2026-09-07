"""Router del panel del administrador (role=ADMIN).

Gestión de organizaciones receptoras: listado, aprobación, rechazo,
desactivación y reactivación (CU-02); y gestión del catálogo maestro de insumos
(§1.2): listar, alta y baja lógica.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import require_role
from app.models import UserRole
from app.schemas.admin import (
    AdminOrgCountsDTO,
    AdminOrgDTO,
    CatalogActionResult,
    CreateInsumoDTO,
    OrgActionResult,
    RejectOrgRequest,
)
from app.schemas.center import CreateEmergencyDTO, EmergencyDTO
from app.schemas.document import OrgDocumentDTO
from app.schemas.org import InsumoCatalogDTO
from app.schemas.pagination import Page
from app.schemas.stats import PlatformStatsDTO, RecentActivityItemDTO
from app.services.activity_service import get_recent_activity as svc_recent_activity
from app.services.admin_service import (
    approve_org as svc_approve,
    close_emergency as svc_close_emergency,
    count_orgs_by_estado as svc_count_orgs,
    create_emergency as svc_create_emergency,
    create_insumo as svc_create_insumo,
    deactivate_org as svc_deactivate,
    delete_insumo as svc_delete_insumo,
    list_emergencies as svc_list_emergencies,
    list_orgs as svc_list,
    reactivate_org as svc_reactivate,
    reject_org as svc_reject,
)
from app.services.stats_service import get_platform_stats as svc_platform_stats
from app.services.document_service import list_org_documents as svc_list_documents
from app.services.org_service import list_insumos_catalog as svc_list_catalog

# La dependencia de rol se aplica a todas las rutas del router.
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)


@router.get("/stats", response_model=PlatformStatsDTO)
def get_stats(db: Session = Depends(get_db)) -> PlatformStatsDTO:
    """Métricas globales de la plataforma (agregados server-side)."""
    return svc_platform_stats(db)


@router.get("/activity", response_model=list[RecentActivityItemDTO])
def get_activity(
    orden: str | None = None,
    db: Session = Depends(get_db),
) -> list[RecentActivityItemDTO]:
    """Feed de actividad (eventos de organizaciones), más recientes primero. El
    parámetro `orden` se acepta por compatibilidad con el contrato del frontend."""
    return svc_recent_activity(db)


@router.get("/orgs", response_model=Page[AdminOrgDTO])
def get_orgs(
    estado: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> Page[AdminOrgDTO]:
    """Página de organizaciones, con filtro opcional por estado."""
    items, total = svc_list(db, estado, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.get("/orgs/counts", response_model=AdminOrgCountsDTO)
def get_orgs_counts(db: Session = Depends(get_db)) -> AdminOrgCountsDTO:
    """Conteo de organizaciones por estado, para las pestañas del panel admin
    (independiente de la paginación de `GET /admin/orgs`)."""
    return AdminOrgCountsDTO(**svc_count_orgs(db))


@router.post("/orgs/{org_id}/approve", response_model=OrgActionResult)
def approve_org(
    org_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> OrgActionResult:
    """Aprueba una organización pendiente (PENDIENTE → ACTIVA)."""
    svc_approve(db, org_id)
    return OrgActionResult()


@router.post("/orgs/{org_id}/reject", response_model=OrgActionResult)
def reject_org(
    org_id: uuid.UUID,
    payload: RejectOrgRequest | None = None,
    db: Session = Depends(get_db),
) -> OrgActionResult:
    """Rechaza una organización pendiente (PENDIENTE → RECHAZADA)."""
    svc_reject(db, org_id, payload.motivo if payload else None)
    return OrgActionResult()


@router.post("/orgs/{org_id}/deactivate", response_model=OrgActionResult)
def deactivate_org(
    org_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> OrgActionResult:
    """Desactiva una organización activa (ACTIVA → INACTIVA)."""
    svc_deactivate(db, org_id)
    return OrgActionResult()


@router.post("/orgs/{org_id}/reactivate", response_model=OrgActionResult)
def reactivate_org(
    org_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> OrgActionResult:
    """Reactiva una organización inactiva (INACTIVA → ACTIVA)."""
    svc_reactivate(db, org_id)
    return OrgActionResult()


@router.get("/orgs/{org_id}/documents", response_model=list[OrgDocumentDTO])
def get_org_documents(
    org_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[OrgDocumentDTO]:
    """Lista los documentos de respaldo de una org con URLs firmadas de descarga."""
    return svc_list_documents(db, org_id)


# --- Catálogo de insumos (§1.2) ---


@router.get("/catalog", response_model=list[InsumoCatalogDTO])
def get_catalog(db: Session = Depends(get_db)) -> list[InsumoCatalogDTO]:
    """Catálogo de insumos activos (mismo listado que consumen las orgs)."""
    return svc_list_catalog(db)


@router.post(
    "/catalog",
    response_model=InsumoCatalogDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_insumo(
    payload: CreateInsumoDTO,
    db: Session = Depends(get_db),
) -> InsumoCatalogDTO:
    """Alta de un insumo. 409 si el nombre ya existe activo; reactiva si estaba dado de baja."""
    return svc_create_insumo(db, payload)


@router.delete("/catalog/{insumo_id}", response_model=CatalogActionResult)
def delete_insumo(
    insumo_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> CatalogActionResult:
    """Baja lógica de un insumo. 404 si no existe/ya inactivo; 409 si tiene needs activas."""
    return svc_delete_insumo(db, insumo_id)


# --- Gestión de emergencias (crear / listar / cerrar) ---


@router.get("/emergencies", response_model=list[EmergencyDTO])
def list_emergencies(
    estado: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[EmergencyDTO]:
    """Emergencias para gestión: activas y cerradas (historial). `?estado=` filtra
    opcionalmente (`activa`/`cerrada`); valor inválido → 422."""
    return svc_list_emergencies(db, estado)


@router.post(
    "/emergencies", response_model=EmergencyDTO, status_code=status.HTTP_201_CREATED
)
def create_emergency(
    payload: CreateEmergencyDTO,
    db: Session = Depends(get_db),
) -> EmergencyDTO:
    """Crea una emergencia (nace `activa`, sin centros). 422 validación."""
    return svc_create_emergency(db, payload)


@router.post("/emergencies/{emergency_id}/close", response_model=EmergencyDTO)
def close_emergency(
    emergency_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> EmergencyDTO:
    """Cierra una emergencia (`activa → cerrada`), sin cascada. 404 si no existe;
    409 si ya estaba cerrada."""
    return svc_close_emergency(db, emergency_id)
