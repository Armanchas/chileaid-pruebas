"""Router de lectura de emergencias para el donante/público.

Sin dependencia de rol: las emergencias activas y sus agregados (cobertura
promedio, total de centros) son información pública del dashboard del donante.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.center import EmergencyDTO
from app.services.center_service import list_active_emergencies

router = APIRouter(prefix="/emergencies", tags=["emergencies"])


@router.get("", response_model=list[EmergencyDTO])
def get_emergencies(
    estado: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[EmergencyDTO]:
    """Emergencias activas con agregados derivados.

    Hoy solo se exponen las activas (`getActiveEmergencies`); el parámetro
    `estado` se acepta por compatibilidad con el contrato del frontend
    (`?estado=activa`) pero el resultado ya viene filtrado a activas.
    """
    return list_active_emergencies(db)
