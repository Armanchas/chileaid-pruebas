"""Catálogo de insumos (gestionado por el admin, CU-? / adminCatalogService).

Es la lista maestra de artículos donables; cada necesidad de un centro referencia
un insumo del catálogo. La `categoria` alimenta el filtro del mapa (RF-06).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import Enum as SAEnum
from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import InsumoCategory

if TYPE_CHECKING:
    from .need import Need


class Insumo(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "insumos"

    nombre: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    categoria: Mapped[InsumoCategory] = mapped_column(
        SAEnum(InsumoCategory, name="insumo_category", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    # Unidad de medida (kg, litros, unidades…), para la cantidad de las necesidades.
    unidad: Mapped[str] = mapped_column(String(40), nullable=False)

    # Soft-delete: el admin da de baja un insumo sin borrar la fila (preserva el
    # unique de `nombre` y las needs históricas que lo referencian). Solo los
    # `activo=True` se listan/solicitan.
    activo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )

    needs: Mapped[list[Need]] = relationship(back_populates="insumo")
