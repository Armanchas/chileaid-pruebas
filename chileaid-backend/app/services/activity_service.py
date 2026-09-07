"""Feed de actividad del dashboard admin (tabla `activity_log`).

`record_activity` añade un evento a la sesión (NO hace commit: lo hace el flujo
que lo llama, dentro de su misma transacción — registro/aprobación/rechazo de org).
`get_recent_activity` lee el feed, más recientes primero.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ActivityLog, ActivityType
from app.schemas.stats import RecentActivityItemDTO

# Cantidad de eventos que muestra el feed del dashboard.
_FEED_LIMIT = 20


def record_activity(
    db: Session,
    tipo: ActivityType,
    descripcion: str,
    organization_id: uuid.UUID | None = None,
) -> None:
    """Registra un evento (snapshot inmutable). El caller controla el commit."""
    db.add(
        ActivityLog(
            tipo=tipo, descripcion=descripcion, organization_id=organization_id
        )
    )


def get_recent_activity(db: Session) -> list[RecentActivityItemDTO]:
    """Eventos recientes del feed, más nuevos primero (máx. `_FEED_LIMIT`)."""
    rows = db.scalars(
        select(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(_FEED_LIMIT)
    ).all()
    return [
        RecentActivityItemDTO(
            id=str(r.id),
            tipo=r.tipo.value,
            descripcion=r.descripcion,
            fecha=r.created_at.date().isoformat(),
        )
        for r in rows
    ]
