"""Schemas de inventario/distribución de la organización (CU-08).

Espejo del contrato del frontend (`distributionService.ts`). El **stock** es
derivado (recibido − distribuido, calculado en el service); un **lote** es una
salida de stock ya registrada (hecho inmutable). Claves compuestas en camelCase.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import LotSalida
from app.schemas.org import RequiredText


class StockItemDTO(BaseModel):
    """Stock disponible de un insumo en el centro (recibido − distribuido)."""

    insumo_id: str = Field(alias="insumoId")
    insumo_nombre: str = Field(alias="insumoNombre")
    categoria: str  # value de InsumoCategory
    unidad: str
    cantidad_disponible: int = Field(alias="cantidadDisponible")

    model_config = ConfigDict(populate_by_name=True)


class DistributionLotDTO(BaseModel):
    """Lote distribuido: una salida de stock registrada."""

    id: str
    insumo_id: str = Field(alias="insumoId")
    insumo_nombre: str = Field(alias="insumoNombre")
    categoria: str
    unidad: str
    cantidad: int
    tipo: str  # value de LotSalida (enviado_a_terreno | entregado_a_beneficiario)
    destino: str
    fecha: str = Field()  # ISO YYYY-MM-DD

    model_config = ConfigDict(populate_by_name=True)


class CreateLotDTO(BaseModel):
    """Body de `POST /org/lots`: registrar una salida de stock.

    Se keyea por `insumoId` (no por nombre); la cantidad debe ser > 0 y no superar
    el stock disponible (validado en el service). `tipo` debe ser una salida
    permitida por el tipo de centro.
    """

    insumo_id: uuid.UUID = Field(alias="insumoId")
    cantidad: int = Field(gt=0)
    tipo: LotSalida
    destino: RequiredText

    model_config = ConfigDict(populate_by_name=True)
