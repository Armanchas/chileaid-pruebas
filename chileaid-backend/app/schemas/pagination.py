"""Envelope genérico de paginación (§2.6), reusado por los listados que puedan
crecer (`GET /admin/orgs`, `GET /donations`)."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """`items` es la página pedida; `total` es el conteo de la query completa
    (con los mismos filtros, sin `limit`/`offset`), para que el cliente pueda
    calcular el número de páginas."""

    items: list[T]
    total: int
    limit: int
    offset: int
