"""Schemas de la recepción de donaciones por la organización (CU-07).

La organización confirma físicamente las donaciones comprometidas: las
`pendiente` de su centro pasan a `recibido` e ingresan a `cantidad_recibida`.
Claves compuestas en camelCase (alias); internamente snake_case
(`populate_by_name=True`).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ReceptionItemDTO(BaseModel):
    """Línea de una recepción pendiente: insumo y cantidad comprometida."""

    need_id: str = Field(alias="needId")
    insumo_nombre: str = Field(alias="insumoNombre")
    cantidad: int

    model_config = ConfigDict(populate_by_name=True)


class PendingReceptionDTO(BaseModel):
    """Donación `pendiente` del centro de la org, lista para confirmar (CU-07)."""

    donation_id: str = Field(alias="donationId")
    codigo_seguimiento: str = Field(alias="codigoSeguimiento")
    items: list[ReceptionItemDTO]
    created_at: str = Field(alias="createdAt")  # ISO 8601

    model_config = ConfigDict(populate_by_name=True)


class ConfirmReceptionRequest(BaseModel):
    """Body de `POST /org/receptions/confirm`: el código de seguimiento a confirmar."""

    codigo: str

    model_config = ConfigDict(populate_by_name=True)


class ConfirmReceptionResult(BaseModel):
    """Resultado de confirmar una recepción: la donación queda `recibido`."""

    success: bool
    codigo_seguimiento: str = Field(alias="codigoSeguimiento")
    estado: str  # value de DonationStatus (recibido tras confirmar)

    model_config = ConfigDict(populate_by_name=True)
