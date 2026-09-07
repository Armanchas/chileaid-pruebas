"""Schemas Pydantic del panel de administración: validación de orgs (CU-02) y
gestión del catálogo de insumos (§1.2)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.models import InsumoCategory
from app.schemas.org import RequiredText


class AdminOrgDTO(BaseModel):
    """Organización vista desde el panel del administrador.

    Claves compuestas en camelCase (alias), igual que el contrato del frontend.
    """

    id: str
    nombre: str
    tipo: str
    rut: str | None
    contacto_nombre: str | None = Field(alias="contactoNombre")
    email: str
    telefono: str | None
    region: str | None
    documentacion: str
    estado: str
    fecha_registro: str = Field(alias="fechaRegistro")
    motivo_rechazo: str | None = Field(None, alias="motivoRechazo")

    model_config = ConfigDict(populate_by_name=True)


class AdminOrgCountsDTO(BaseModel):
    """Conteo de organizaciones por estado, para las pestañas del panel admin.
    Independiente de la paginación de `GET /admin/orgs`."""

    todas: int
    pendiente: int
    activa: int
    rechazada: int
    inactiva: int


class RejectOrgRequest(BaseModel):
    """Cuerpo opcional del rechazo: motivo legible para la organización."""

    motivo: str | None = None


class OrgActionResult(BaseModel):
    """Confirmación mínima de una acción de moderación."""

    success: bool = True


class CreateInsumoDTO(BaseModel):
    """Body de `POST /admin/catalog`: alta de un insumo en el catálogo maestro.

    `categoria` se valida contra el enum `InsumoCategory` (422 si llega un value
    fuera del catálogo). `nombre`/`unidad` no pueden quedar vacíos.
    """

    nombre: RequiredText
    categoria: InsumoCategory
    unidad: RequiredText


class CatalogActionResult(BaseModel):
    """Confirmación mínima de una acción del admin sobre el catálogo."""

    success: bool = True
