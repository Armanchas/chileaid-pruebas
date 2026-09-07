"""Centro de acopio: punto físico georreferenciado de una organización.

- RF-05: coordenadas (lat/lng) + dirección para desplegar en el mapa.
- `estado` persiste solo la OPERATIVIDAD del centro (activo/cerrado).
- RF-07: la SATURACIÓN visual del marcador ('en_capacidad'/'critico'/'cerrado')
  y `cobertura` (0-100) NO se almacenan: se derivan de las necesidades/donaciones
  del centro en el service. Aquí solo guardamos lo persistente.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import CenterStatus

if TYPE_CHECKING:
    from .emergency import Emergency
    from .need import Need
    from .organization import Organization


class Center(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "centers"

    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    # Un centro puede existir sin emergencia asignada todavía (FK nullable).
    emergency_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("emergencies.id", ondelete="SET NULL")
    )

    zona: Mapped[str] = mapped_column(String(200), nullable=False)
    direccion: Mapped[str] = mapped_column(String(300), nullable=False)
    horario_atencion: Mapped[str | None] = mapped_column(String(200))  # tarjeta del mapa (CU-11)

    # --- Georreferenciación (RF-05) ---
    # Numeric(9,6): ~0.1 m de precisión, suficiente para mapas. Nullable hasta
    # que la API de mapas geocodifica la dirección. (Alternativa: PostGIS
    # `Geography(POINT)` si se requieren consultas espaciales por radio.)
    latitud: Mapped[float | None] = mapped_column(Numeric(9, 6))
    longitud: Mapped[float | None] = mapped_column(Numeric(9, 6))

    # --- Operatividad (persistida) ---
    # Si el centro opera (ACTIVO) o ya no recibe donaciones (CERRADO).
    # La saturación visual del mapa (RF-07) NO se guarda aquí: se deriva de la
    # cobertura en el service y se entrega en el `estado` del CenterDTO.
    estado: Mapped[CenterStatus] = mapped_column(
        SAEnum(CenterStatus, name="center_status", values_callable=lambda e: [m.value for m in e]),
        default=CenterStatus.ACTIVO,
        nullable=False,
    )

    # --- Relaciones ---
    organization: Mapped[Organization] = relationship(back_populates="centers")
    emergency: Mapped[Emergency | None] = relationship(back_populates="centers")
    needs: Mapped[list[Need]] = relationship(
        back_populates="center", cascade="all, delete-orphan"
    )
