"""Router de estadísticas públicas del landing (sin token).

Agregados en tiempo real de la operación nacional (centros operativos, donantes
activos, aportes registrados, emergencias activas). Los agregados del admin viven
en `/admin/stats` (router admin, role=admin).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.stats import StatItemDTO
from app.services.stats_service import get_public_stats

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=list[StatItemDTO])
def get_stats(db: Session = Depends(get_db)) -> list[StatItemDTO]:
    """4 métricas públicas del landing (valor crudo + label; el frontend formatea)."""
    return get_public_stats(db)
