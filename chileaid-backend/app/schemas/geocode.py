"""Schema de la respuesta de geocodificación (`GET /geocode`, RF-05)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class GeocodeResultDTO(BaseModel):
    """Coordenadas sugeridas para una dirección + su nombre resuelto."""

    latitud: float
    longitud: float
    display_name: str = Field(alias="displayName")

    model_config = ConfigDict(populate_by_name=True)
