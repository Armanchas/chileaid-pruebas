"""Emergencia/catástrofe que agrupa centros de acopio (relación 1-a-N).

`cobertura` y `totalCentros` que consume el frontend son agregados DERIVADOS
de los centros (no se almacenan): se calculan en el service/query.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date
from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import EmergencyStatus, EmergencyType

if TYPE_CHECKING:
    from .center import Center


class Emergency(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "emergencies"

    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[EmergencyType] = mapped_column(
        SAEnum(EmergencyType, name="emergency_type", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    zona: Mapped[str] = mapped_column(String(200), nullable=False)
    # Solo fecha (el contrato la serializa como 'YYYY-MM-DD', sin hora).
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[EmergencyStatus] = mapped_column(
        SAEnum(
            EmergencyStatus,
            name="emergency_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=EmergencyStatus.ACTIVA,
        nullable=False,
    )

    centers: Mapped[list[Center]] = relationship(back_populates="emergency")
