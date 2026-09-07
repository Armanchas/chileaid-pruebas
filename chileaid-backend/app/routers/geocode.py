"""Router de geocodificación (RF-05): dirección → coordenadas sugeridas.

Alimenta el selector de mapa del `OrgCenterForm` (botón "ubicar por dirección"):
el frontend envía la dirección tipeada y recibe un punto para centrar el mapa y
posicionar el pin, que la org puede ajustar. El punto exacto lo decide el click
en el mapa; esto es solo la sugerencia inicial.

Gateado con auth de organización (`get_current_organization_id`): solo lo usan
las orgs al crear/editar su centro; evita exponer un proxy abierto a Nominatim.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query

from app.dependencies.auth import get_current_organization_id
from app.schemas.geocode import GeocodeResultDTO
from app.services import geocoding_service

router = APIRouter(prefix="/geocode", tags=["geocode"])


@router.get("", response_model=GeocodeResultDTO | None)
def geocode_address(
    q: str = Query(..., min_length=3, description="Dirección a geocodificar"),
    _org_id: uuid.UUID = Depends(get_current_organization_id),
) -> GeocodeResultDTO | None:
    """Geocodifica `q`; devuelve el punto sugerido o `null` si no se encontró."""
    hit = geocoding_service.geocode(q)
    if hit is None:
        return None
    return GeocodeResultDTO(
        latitud=hit.latitud,
        longitud=hit.longitud,
        displayName=hit.display_name,
    )
