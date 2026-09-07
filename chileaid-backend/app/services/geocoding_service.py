"""Geocodificación de direcciones vía Nominatim (OpenStreetMap).

Convierte una dirección de texto en coordenadas (lat, lng). Se usa en dos
lugares: como **fallback** al crear/editar un centro sin coordenadas
(`org_service`), y detrás del endpoint `GET /geocode` que alimenta el selector de
mapa del frontend (RF-05).

Falla **en silencio** (devuelve `None`) ante error de red, timeout, respuesta no
parseable o dirección no encontrada: la geocodificación es una comodidad y nunca
debe tumbar el alta de un centro.

Política de Nominatim: se envía un `User-Agent` que identifica la app y se sesga
la búsqueda a Chile (`countrycodes=cl`). Para volumen alto, apuntar
`NOMINATIM_URL` a una instancia self-host.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Nominatim pide requests cortas y responsables; 5 s es holgado y evita colgar
# el alta de un centro si el servicio no responde.
_TIMEOUT = 5.0


@dataclass(frozen=True)
class GeocodeHit:
    """Resultado de geocodificar una dirección."""

    latitud: float
    longitud: float
    display_name: str


def geocode(query: str) -> GeocodeHit | None:
    """Devuelve el primer match de `query` como `GeocodeHit`, o `None`.

    `None` cubre todos los casos no felices (query vacía, sin resultados, error
    de red/timeout, JSON inesperado) para que el llamador no tenga que
    distinguirlos: siempre es "no pude geocodificar".
    """
    q = query.strip()
    if not q:
        return None

    try:
        res = httpx.get(
            f"{settings.NOMINATIM_URL.rstrip('/')}/search",
            params={"q": q, "format": "jsonv2", "limit": 1, "countrycodes": "cl"},
            headers={"User-Agent": settings.NOMINATIM_USER_AGENT},
            timeout=_TIMEOUT,
        )
        res.raise_for_status()
        data = res.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("Geocoding falló para %r: %s", q, exc)
        return None

    if not data:
        return None

    first = data[0]
    try:
        return GeocodeHit(
            latitud=float(first["lat"]),
            longitud=float(first["lon"]),
            display_name=str(first.get("display_name", "")),
        )
    except (KeyError, TypeError, ValueError) as exc:
        logger.warning("Respuesta de Nominatim inesperada para %r: %s", q, exc)
        return None
