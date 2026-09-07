"""Lógica geográfica: catálogo de regiones de Chile y su validación.

`REGIONES_CHILE` replica la lista canónica del frontend
(`donorDashboardService.REGIONES_CHILE`) SIN el valor centinela
'Todas las regiones', que es un filtro de UI y no una región real. Es la fuente
de verdad para validar la `region` en el registro de organizaciones (CU-01).

⚠️ Los nombres deben calzar EXACTAMENTE con la lista del frontend (contrato de
datos); un valor distinto rompería el `<select>` de región del cliente.
"""

from __future__ import annotations

REGIONES_CHILE: tuple[str, ...] = (
    "Arica y Parinacota",
    "Tarapacá",
    "Antofagasta",
    "Atacama",
    "Coquimbo",
    "Valparaíso",
    "Metropolitana",
    "O'Higgins",
    "Maule",
    "Ñuble",
    "Biobío",
    "La Araucanía",
    "Los Ríos",
    "Los Lagos",
    "Aysén",
    "Magallanes",
)


def is_valid_region(region: str) -> bool:
    """True si `region` es una región chilena válida (no el centinela de UI)."""
    return region in REGIONES_CHILE
