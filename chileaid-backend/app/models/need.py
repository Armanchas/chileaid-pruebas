"""Necesidad: solicitud de un insumo en un centro. Es la unidad de la barra de
progreso y el punto donde se controla la concurrencia (RF-02).

Cantidades persistidas (la `cobertura` 0-100 se DERIVA de ellas):
- `cantidad_requerida`  : meta de recolección.
- `cantidad_comprometida`: suma reservada por aportes PENDIENTE
                           (lo que avanza la barra y bloquea sobrestock).
- `cantidad_recibida`   : confirmada físicamente (CU-07).

Control de concurrencia (RF-02) — BLOQUEO OPTIMISTO:
La columna `version_id` + `version_id_col` hace que cada UPDATE valide la
versión leída; si dos donantes comprometen a la vez sobre la misma necesidad,
el segundo UPDATE falla con StaleDataError y el service reintenta sobre el
estado fresco. Así se evita el sobrestock sin mantener locks abiertos.
(Alternativa pesimista, a nivel de query en el service:
    select(Need).where(...).with_for_update()
 que toma `SELECT ... FOR UPDATE` y serializa los compromisos concurrentes.)
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import NeedStatus, Urgencia

if TYPE_CHECKING:
    from .center import Center
    from .catalog import Insumo
    from .donation import DonationItem


class Need(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "needs"
    __table_args__ = (
        # La barra nunca debe sobrepasar la meta (refuerza RF-04 en la BD).
        CheckConstraint(
            "cantidad_comprometida <= cantidad_requerida",
            name="ck_need_no_sobrestock",
        ),
    )

    center_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("centers.id", ondelete="CASCADE"), nullable=False
    )
    insumo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("insumos.id", ondelete="RESTRICT"), nullable=False
    )

    cantidad_requerida: Mapped[int] = mapped_column(Integer, nullable=False)
    cantidad_comprometida: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cantidad_recibida: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    urgencia: Mapped[Urgencia] = mapped_column(
        SAEnum(Urgencia, name="urgencia", values_callable=lambda e: [m.value for m in e]),
        default=Urgencia.MEDIA,
        nullable=False,
    )
    estado: Mapped[NeedStatus] = mapped_column(
        SAEnum(NeedStatus, name="need_status", values_callable=lambda e: [m.value for m in e]),
        default=NeedStatus.ACTIVA,
        nullable=False,
    )

    # Contador de versión para el bloqueo optimista (RF-02). Ver docstring.
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    __mapper_args__ = {"version_id_col": version_id}

    # --- Relaciones ---
    center: Mapped[Center] = relationship(back_populates="needs")
    insumo: Mapped[Insumo] = relationship(back_populates="needs")
    donation_items: Mapped[list[DonationItem]] = relationship(back_populates="need")
