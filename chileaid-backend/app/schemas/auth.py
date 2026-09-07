"""Schemas Pydantic del flujo de autenticación: login (CU-09) y registro (CU-01).

Claves compuestas en camelCase (alias), igual que el contrato del frontend;
internamente se trabajan en snake_case (`populate_by_name=True`).
"""

from __future__ import annotations

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from app.models import TipoCentro
from app.schemas.org import RequiredText
from app.services.geo_service import REGIONES_CHILE, is_valid_region


class LoginRequest(BaseModel):
    """Cuerpo JSON del login. Espejo de `AuthCredentials` del frontend."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeDTO(BaseModel):
    """Respuesta de `GET /auth/me` (§1.7): identidad verificada server-side.

    A diferencia del decode client-side del JWT (`utils/jwt.ts` en el
    frontend, sin validar firma), este endpoint sí valida la firma/expiración
    (vía `get_current_user`) y resuelve `organization_id` fresco desde la BD
    en vez de confiar en el claim del token.
    """

    id: str
    role: str
    organization_id: str | None = Field(None, alias="organizationId")

    model_config = ConfigDict(populate_by_name=True)


class OrgRegisterRequest(BaseModel):
    """Cuerpo JSON del registro de una organización receptora (CU-01).

    Crea la cuenta-representante (`User` role=org) y la `Organization` (estado
    PENDIENTE). `nombre`/`direccion`/`contactoNombre`/`telefono`/`region` son
    obligatorios y no vacíos; `rut` es opcional. La `region` debe pertenecer al
    catálogo nacional (`REGIONES_CHILE`); `password` y `confirmPassword` deben
    coincidir. No se piden documentos ni comuna (fuera de alcance del MVP).
    """

    nombre: RequiredText
    tipo_centro: TipoCentro = Field(alias="tipoCentro")
    rut: str | None = None
    direccion: RequiredText
    contacto_nombre: RequiredText = Field(alias="contactoNombre")
    email: EmailStr
    telefono: RequiredText
    region: RequiredText
    password: str = Field(min_length=1)
    confirm_password: str = Field(alias="confirmPassword", min_length=1)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("region")
    @classmethod
    def _region_en_catalogo(cls, v: str) -> str:
        # `v` ya viene recortado por RequiredText; rechazamos el centinela de UI
        # y cualquier valor fuera del catálogo nacional.
        if not is_valid_region(v):
            raise ValueError(
                f"Región inválida; debe ser una de: {', '.join(REGIONES_CHILE)}"
            )
        return v

    @model_validator(mode="after")
    def _passwords_coinciden(self) -> "OrgRegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("Las contraseñas no coinciden")
        return self


class RegisterDonorRequest(BaseModel):
    """Cuerpo JSON del registro de un donante particular (CU-XX).

    Crea la cuenta de inmediato (role=DONOR) y emite token: el donante no
    necesita aprobación previa, a diferencia del flujo de org. `password` y
    `confirmPassword` deben coincidir; mínimo 6 caracteres.
    """

    nombre: RequiredText
    apellido: RequiredText
    email: EmailStr
    password: str = Field(min_length=6)
    confirm_password: str = Field(alias="confirmPassword", min_length=6)

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def _passwords_coinciden(self) -> "RegisterDonorRequest":
        if self.password != self.confirm_password:
            raise ValueError("Las contraseñas no coinciden")
        return self


class RegisterResult(BaseModel):
    """Confirmación mínima del registro. Espejo de `RegisterResult` del frontend.

    `token` viene poblado en el registro de organización (para subir el
    documento de respaldo en el mismo flujo, antes de ir a `/login`) aunque la
    org nazca Pendiente (verificación del admin, CU-02); en el registro de
    donante también viaja token, ya que esa cuenta no requiere aprobación.
    """

    success: bool = True
    token: str | None = None
