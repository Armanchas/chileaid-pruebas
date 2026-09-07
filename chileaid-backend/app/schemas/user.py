"""Schemas del perfil del donante particular (AC-01, `profileService`).

Espejo del `DonorProfileDTO` del frontend. Claves compuestas en **camelCase**
(alias), internamente snake_case (`populate_by_name=True`); FastAPI serializa por
alias. Gemelo simplificado de `OrgProfileDTO`: el donante solo edita sus datos
personales (`nombre`, `apellido`, `email`), no hay contacto/región.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Texto obligatorio (recorta espacios + exige ≥1 carácter no-blanco → 422 si
# queda vacío). Reutiliza el alias del módulo gemelo en vez de redefinirlo.
from app.schemas.org import RequiredText


class DonorProfileDTO(BaseModel):
    """Perfil del donante autenticado.

    `fechaRegistro` es `user.created_at` truncado a fecha (YYYY-MM-DD).
    """

    nombre: str
    apellido: str
    email: EmailStr
    fecha_registro: str = Field(alias="fechaRegistro")  # ISO YYYY-MM-DD

    model_config = ConfigDict(populate_by_name=True)


class UpdateDonorProfileDTO(BaseModel):
    """Body de `PUT /me/donor`: edición de los datos personales del donante.

    Los tres campos son obligatorios y no pueden quedar vacíos; `email` se valida
    con formato (EmailStr).
    """

    nombre: RequiredText = Field(alias="nombre")
    apellido: RequiredText = Field(alias="apellido")
    email: EmailStr = Field(alias="email")

    model_config = ConfigDict(populate_by_name=True)
