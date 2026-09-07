"""Lote de distribución: una salida de stock del centro (CU-08).

Un lote registra que una cantidad de un insumo dejó el centro hacia un destino
(a terreno o entregada a un beneficiario). Es un **hecho inmutable** (una salida
ocurrida), sin ciclo de estados.

El stock disponible NO se persiste: se DERIVA como
`Σ need.cantidad_recibida (por insumo) − Σ DistributionLot.cantidad (por insumo)`
en el service (misma filosofía que `cobertura`). Este modelo solo guarda las
salidas; las entradas ya viven en `need.cantidad_recibida` (recepción, CU-07).
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import LotSalida

if TYPE_CHECKING:
    from .catalog import Insumo
    from .center import Center


class DistributionLot(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "distribution_lots"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_lot_cantidad_positiva"),
    )

    center_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("centers.id", ondelete="CASCADE"), nullable=False
    )
    insumo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("insumos.id", ondelete="RESTRICT"), nullable=False
    )
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo: Mapped[LotSalida] = mapped_column(
        SAEnum(LotSalida, name="lot_salida", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    destino: Mapped[str] = mapped_column(String(200), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)

    # --- Relaciones ---
    center: Mapped[Center] = relationship()
    insumo: Mapped[Insumo] = relationship()
