"""Router de lectura de centros para el donante/público (CU-04, CU-10/CU-11).

Sin dependencia de rol: el listado, el detalle y las necesidades de un centro son
información pública que el donante consulta antes de comprometer un aporte.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.center import CenterDetailDTO, CenterDTO
from app.schemas.org import NeedDTO
from app.services.center_service import (
    get_center_detail,
    list_active_needs_for_center,
    list_centers,
)

router = APIRouter(prefix="/centers", tags=["centers"])


@router.get("", response_model=list[CenterDTO])
def get_centers(
    region: str | None = Query(default=None),
    tipo: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    emergencia_id: str | None = Query(default=None, alias="emergenciaId"),
    orden: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[CenterDTO]:
    """Listado público de centros con filtros (CU-10/CU-11).

    Filtros opcionales en AND: `region`, `tipo` (tipo de centro), `estado`
    (saturación derivada), `emergenciaId`. `orden=cobertura_asc` da los críticos
    primero.
    """
    return list_centers(
        db,
        region=region,
        tipo=tipo,
        estado=estado,
        emergencia_id=emergencia_id,
        orden=orden,
    )


@router.get("/{center_id}", response_model=CenterDetailDTO)
def get_center(
    center_id: uuid.UUID, db: Session = Depends(get_db)
) -> CenterDetailDTO:
    """Detalle público de un centro (CU-04/CU-11). 404 si no existe."""
    return get_center_detail(db, center_id)


@router.get("/{center_id}/needs", response_model=list[NeedDTO])
def get_center_needs(
    center_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[NeedDTO]:
    """Necesidades activas de un centro (CU-04). Público; 404 si el centro no existe."""
    return list_active_needs_for_center(db, center_id)
