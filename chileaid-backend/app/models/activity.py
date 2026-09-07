"""Registro de actividad de la plataforma (feed del dashboard admin).

Cada fila es un **evento inmutable** del ciclo de vida de una organización
(registro, aprobación, rechazo), escrito en el momento en que ocurre. La
`descripcion` es un snapshot al momento del evento (no se regenera al leer), como
`DistributionLot`. El admin no reconstruye historia derivándola de
`organizations` (que solo guarda el estado actual): la lee de aquí.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import ActivityType

if TYPE_CHECKING:
    from .organization import Organization


class ActivityLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "activity_log"

    tipo: Mapped[ActivityType] = mapped_column(
        SAEnum(ActivityType, name="activity_type", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    descripcion: Mapped[str] = mapped_column(String(300), nullable=False)
    # Nullable + SET NULL: el feed conserva el evento aunque la org se borre.
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL")
    )

    organization: Mapped[Organization | None] = relationship()
