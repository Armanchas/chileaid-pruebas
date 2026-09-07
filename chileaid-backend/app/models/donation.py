"""Aporte comprometido por un donante (CU-05, CU-06, CU-07).

Modelo header + items: una `Donation` representa una entrega completa de un
donante (su unidad de trazabilidad), y sus `DonationItem` detallan la cantidad
comprometida contra cada necesidad. Así una sola entrega (un código QR) puede
cubrir varias necesidades de un centro.

RF-01 (trazabilidad): cada aporte lleva un `codigo_seguimiento` único
(alfanumérico, prefijo 'CA-') que se materializa como QR. La generación del
código es lógica de negocio (service); aquí solo se persiste con `unique=True`.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import DonationStatus, MotivoCancelacion

if TYPE_CHECKING:
    from .need import Need
    from .user import User


class Donation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "donations"

    donor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # RF-01: código único de trazabilidad (QR / alfanumérico, prefijo 'CA-').
    codigo_seguimiento: Mapped[str] = mapped_column(
        String(40), unique=True, index=True, nullable=False
    )

    estado: Mapped[DonationStatus] = mapped_column(
        SAEnum(DonationStatus, name="donation_status", values_callable=lambda e: [m.value for m in e]),
        default=DonationStatus.PENDIENTE,
        nullable=False,
    )
    # Momento en que la org escanea/confirma la recepción (CU-07); null hasta entonces.
    confirmado_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # --- Relaciones ---
    donor: Mapped[User] = relationship(back_populates="donations")
    items: Mapped[list[DonationItem]] = relationship(
        back_populates="donation", cascade="all, delete-orphan"
    )


class DonationItem(UUIDPrimaryKeyMixin, Base):
    """Línea de una donación: cantidad comprometida contra una necesidad concreta."""

    __tablename__ = "donation_items"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_donation_item_cantidad_positiva"),
    )

    donation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("donations.id", ondelete="CASCADE"), nullable=False
    )
    need_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("needs.id", ondelete="RESTRICT"), nullable=False
    )
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)

    # Soft-cancel a nivel de ítem (mismo patrón que `Insumo.activo`): cancelar =
    # `activo = False`. La donación padre pasa a CANCELADA solo cuando todos sus
    # ítems quedan inactivos; si sobrevive al menos uno, sigue PENDIENTE.
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Por qué se canceló (null mientras `activo=True`). Deja que el tracking
    # muestre el mensaje correcto según quién lo disparó (donante vs cierre de need).
    motivo_cancelacion: Mapped[MotivoCancelacion | None] = mapped_column(
        SAEnum(
            MotivoCancelacion,
            name="motivo_cancelacion",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=True,
    )

    # --- Relaciones ---
    donation: Mapped[Donation] = relationship(back_populates="items")
    need: Mapped[Need] = relationship(back_populates="donation_items")
