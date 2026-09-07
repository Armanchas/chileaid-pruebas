"""Router de la Organización Receptora (role=ORG).

Panel del centro de la org y la gestión de sus necesidades (CU-03). La org se
resuelve del JWT (claim `organization_id`), nunca de la URL.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_organization_id, require_role
from app.models import User, UserRole
from app.schemas.document import (
    DocumentUploadURLRequest,
    DocumentUploadURLResponse,
    OrgDocumentDTO,
    SaveDocumentRequest,
)
from app.schemas.org import (
    CenterCreateDTO,
    CenterUpdateDTO,
    InsumoCatalogDTO,
    NeedCreateDTO,
    NeedDTO,
    NeedUpdateDTO,
    OrgCenterDTO,
    OrgProfileDTO,
    UpdateOrgProfileDTO,
)
from app.schemas.distribution import (
    CreateLotDTO,
    DistributionLotDTO,
    StockItemDTO,
)
from app.schemas.reception import (
    ConfirmReceptionRequest,
    ConfirmReceptionResult,
    PendingReceptionDTO,
)
from app.services.document_service import (
    get_upload_url as svc_get_upload_url,
    list_org_documents as svc_list_documents,
    save_document as svc_save_document,
)
from app.services.org_service import (
    build_need_dto,
    build_org_center_dto,
    build_org_profile_dto,
    close_need,
    create_center_for_organization,
    create_need,
    get_center_by_organization,
    get_insumo,
    get_need_in_center,
    get_organization,
    list_insumos_catalog,
    update_center_for_organization,
    update_need,
    update_org_profile,
)
from app.services.distribution_service import (
    create_lot as svc_create_lot,
    get_lots as svc_get_lots,
    get_stock as svc_get_stock,
)
from app.services.reception_service import (
    confirm_reception,
    list_pending_receptions,
)

router = APIRouter(prefix="/org", tags=["org"])


@router.get("/center", response_model=OrgCenterDTO)
def get_org_center(
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
) -> OrgCenterDTO:
    """Centro de acopio de la organización autenticada, con necesidades y totales."""
    center = get_center_by_organization(db, organization_id)
    if center is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La organización aún no tiene un centro registrado",
        )
    return build_org_center_dto(center)


@router.post(
    "/center", response_model=OrgCenterDTO, status_code=status.HTTP_201_CREATED
)
def create_org_center(
    payload: CenterCreateDTO,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
) -> OrgCenterDTO:
    """Crea el centro de la organización autenticada (CU-08).

    409 si la org ya tiene un centro (la unicidad la hace valer el service);
    422 si las coordenadas vienen incompletas o fuera de rango (Pydantic).
    """
    return create_center_for_organization(db, organization_id, payload)


@router.put("/center", response_model=OrgCenterDTO)
def update_org_center(
    payload: CenterUpdateDTO,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
) -> OrgCenterDTO:
    """Edita el centro de la organización autenticada (CU-08).

    404 si la org aún no tiene centro (en ese caso corresponde POST); 422 si las
    coordenadas vienen incompletas o fuera de rango (Pydantic). No edita `estado`
    ni `emergency_id`.
    """
    return update_center_for_organization(db, organization_id, payload)


@router.get("/profile", response_model=OrgProfileDTO)
def get_org_profile(
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
) -> OrgProfileDTO:
    """Perfil de la organización autenticada (CU-09): identidad + contacto + estado."""
    org = get_organization(db, organization_id)
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La organización no existe",
        )
    return build_org_profile_dto(org)


@router.put("/profile", response_model=OrgProfileDTO)
def update_org_profile_endpoint(
    payload: UpdateOrgProfileDTO,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
) -> OrgProfileDTO:
    """Actualiza los datos de contacto de la organización autenticada (CU-09).

    422 si la validación de Pydantic falla (campos vacíos / email inválido);
    409 si el nuevo email ya está tomado por otra cuenta (lo hace valer el service).
    """
    return update_org_profile(db, organization_id, payload)


@router.get("/needs", response_model=list[NeedDTO])
def get_org_needs(
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
) -> list[NeedDTO]:
    """Necesidades del centro de la organización. Lista vacía si no tiene centro."""
    center = get_center_by_organization(db, organization_id)
    if center is None:
        return []
    return [build_need_dto(n) for n in center.needs]


@router.get("/catalog/insumos", response_model=list[InsumoCatalogDTO])
def get_catalog_insumos(
    # Lectura compartida: la org lo usa para el alta de necesidades y el admin
    # para gestionar el catálogo (la mutación del catálogo sí es solo admin).
    _: User = Depends(require_role(UserRole.ORG, UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> list[InsumoCatalogDTO]:
    """Catálogo de insumos solicitables (con IDs reales) para el alta de necesidades."""
    return list_insumos_catalog(db)


@router.post("/needs", response_model=NeedDTO, status_code=status.HTTP_201_CREATED)
def create_org_need(
    payload: NeedCreateDTO,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
) -> NeedDTO:
    """Crea una necesidad en el centro de la organización autenticada."""
    center = get_center_by_organization(db, organization_id)
    if center is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La organización aún no tiene un centro registrado",
        )
    insumo = get_insumo(db, payload.insumo_id)
    if insumo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El insumo seleccionado no existe en el catálogo",
        )
    return create_need(db, center, insumo, payload)


@router.put("/needs/{need_id}", response_model=NeedDTO)
def update_org_need(
    need_id: uuid.UUID,
    payload: NeedUpdateDTO,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
) -> NeedDTO:
    """Actualiza una necesidad del centro de la organización autenticada."""
    center = get_center_by_organization(db, organization_id)
    if center is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La organización aún no tiene un centro registrado",
        )
    need = get_need_in_center(db, need_id, center)
    if need is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La necesidad no existe o no pertenece a tu centro",
        )
    # Las reglas de edición (409 si está cerrada/completada, 422 si baja de lo
    # comprometido) las hace valer update_need.
    return update_need(db, need, payload)


@router.patch("/needs/{need_id}/cerrar", response_model=NeedDTO)
def close_org_need(
    need_id: uuid.UUID,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
) -> NeedDTO:
    """Cierre manual de una necesidad del centro de la organización (CU-03)."""
    center = get_center_by_organization(db, organization_id)
    if center is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La organización aún no tiene un centro registrado",
        )
    need = get_need_in_center(db, need_id, center)
    if need is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La necesidad no existe o no pertenece a tu centro",
        )
    # La regla 409 (solo se cierra una ACTIVA) la hace valer close_need.
    return close_need(db, need)


@router.get("/receptions/pending", response_model=list[PendingReceptionDTO])
def get_pending_receptions(
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
) -> list[PendingReceptionDTO]:
    """Donaciones pendientes de confirmar del centro de la org (CU-07).

    Lista vacía si la org no tiene centro o no tiene donaciones pendientes.
    """
    return list_pending_receptions(db, organization_id)


@router.post("/receptions/confirm", response_model=ConfirmReceptionResult)
def confirm_reception_endpoint(
    payload: ConfirmReceptionRequest,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
) -> ConfirmReceptionResult:
    """Confirma la recepción de una donación por su código (CU-07).

    404 código inexistente; 403 si no pertenece al centro de la org; 409 si ya
    fue confirmada. En éxito la donación queda `recibido` y cada necesidad suma su
    `cantidad_recibida` (lo hace valer el service).
    """
    return confirm_reception(db, organization_id, payload.codigo)


@router.get("/documents", response_model=list[OrgDocumentDTO])
def list_documents(
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
) -> list[OrgDocumentDTO]:
    """Lista los documentos de respaldo de la org con URLs firmadas de descarga."""
    return svc_list_documents(db, organization_id)


@router.post("/documents/upload-url", response_model=DocumentUploadURLResponse)
def request_upload_url(
    payload: DocumentUploadURLRequest,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
) -> DocumentUploadURLResponse:
    """Devuelve una URL presignada de subida directa a S3 (RF-03, CU-01)."""
    return svc_get_upload_url(organization_id, payload.nombre_archivo, payload.tipo)


@router.post("/documents", response_model=OrgDocumentDTO, status_code=status.HTTP_201_CREATED)
def save_document_record(
    payload: SaveDocumentRequest,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
) -> OrgDocumentDTO:
    """Registra un documento tras su subida exitosa a S3 (RF-03)."""
    return svc_save_document(
        db, organization_id, payload.nombre_archivo, payload.object_key, payload.tipo
    )


# --- Inventario / distribución (CU-08) ---


@router.get("/stock", response_model=list[StockItemDTO])
def get_stock(
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
) -> list[StockItemDTO]:
    """Stock disponible por insumo (recibido − distribuido). `[]` si sin centro."""
    return svc_get_stock(db, organization_id)


@router.get("/lots", response_model=list[DistributionLotDTO])
def get_lots(
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
) -> list[DistributionLotDTO]:
    """Lotes distribuidos del centro, más recientes primero. `[]` si sin centro."""
    return svc_get_lots(db, organization_id)


@router.post("/lots", response_model=DistributionLotDTO, status_code=status.HTTP_201_CREATED)
def create_lot(
    payload: CreateLotDTO,
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    db: Session = Depends(get_db),
) -> DistributionLotDTO:
    """Registra una salida de stock. 404 sin centro / insumo inexistente; 422 si el
    tipo de salida no corresponde al centro o la cantidad supera el disponible."""
    return svc_create_lot(db, organization_id, payload)
