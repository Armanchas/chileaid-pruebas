"""Schemas del aporte del donante (CU-05). Espejo del contrato del frontend.

Claves compuestas en camelCase (alias); internamente snake_case
(`populate_by_name=True`). Una donación es header + items: una entrega con su
código de trazabilidad (`codigoSeguimiento`, RF-01) y N líneas, cada una contra
una necesidad concreta.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field


class DonationItemRequest(BaseModel):
    """Línea del aporte: cuánto se compromete contra una necesidad."""

    need_id: uuid.UUID = Field(alias="needId")
    cantidad: int = Field(gt=0)

    model_config = ConfigDict(populate_by_name=True)


class CreateDonationRequest(BaseModel):
    """Body de `POST /donations`: al menos una línea, cada cantidad > 0."""

    items: list[DonationItemRequest] = Field(min_length=1)

    model_config = ConfigDict(populate_by_name=True)


class DonationItemDTO(BaseModel):
    """Línea del aporte en la respuesta, con el insumo y su centro/organización
    ya resueltos (vía need → insumo / need → center → organization).

    `activo` es False cuando el ítem se canceló (soft-cancel); `motivoCancelacion`
    dice quién lo disparó (`donante` | `cierre_necesidad`), null mientras el ítem
    sigue activo. El tracking usa ambos para el mensaje correcto.
    """

    need_id: str = Field(alias="needId")
    cantidad: int
    insumo_nombre: str = Field(alias="insumoNombre")
    insumo_unidad: str = Field(alias="insumoUnidad")
    centro_nombre: str = Field(alias="centroNombre")
    organizacion_nombre: str = Field(alias="organizacionNombre")
    activo: bool
    motivo_cancelacion: str | None = Field(alias="motivoCancelacion")

    model_config = ConfigDict(populate_by_name=True)


class DonationDTO(BaseModel):
    """Aporte: identificador, código de trazabilidad, estado, ítems y fechas.

    `confirmadoAt` es null mientras el aporte sigue `pendiente`; se llena cuando
    la organización confirma la recepción (CU-07).
    """

    id: str
    codigo_seguimiento: str = Field(alias="codigoSeguimiento")
    estado: str  # value de DonationStatus (pendiente | recibido | cancelada)
    items: list[DonationItemDTO]
    created_at: str = Field(alias="createdAt")  # ISO 8601
    confirmado_at: str | None = Field(alias="confirmadoAt")  # ISO 8601 o null

    model_config = ConfigDict(populate_by_name=True)
