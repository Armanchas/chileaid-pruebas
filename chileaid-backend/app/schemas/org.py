"""Schemas de la Organización Receptora (panel CU-08 / `orgDashboardService`).

Espejo de los DTO del frontend, con la estructura autocontenida del centro +
necesidades + totales. Claves compuestas en **camelCase** (alias), igual que el
contrato del frontend; internamente se trabajan en snake_case
(`populate_by_name=True`) y FastAPI serializa por alias.

⚠️ Naming: SIEMPRE "cobertura", nunca "saturación".
"""

from __future__ import annotations

import uuid
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    model_validator,
)


class InsumoDTO(BaseModel):
    """Datos del insumo del catálogo que referencia una necesidad."""

    nombre: str
    categoria: str  # value del enum InsumoCategory (agua, alimentos, …)
    unidad: str


class InsumoCatalogDTO(BaseModel):
    """Ítem del catálogo de insumos solicitables, con su `id` real (UUID).

    Es la fuente del `<select>` al crear una necesidad: el frontend envía este
    `id` como `insumoId` en `POST /org/needs`.
    """

    id: str
    nombre: str
    categoria: str  # value del enum InsumoCategory
    unidad: str
    activo: bool = True  # soft-delete: los listados solo traen activos


class NeedDTO(BaseModel):
    """Necesidad de un centro: la unidad de la barra de progreso.

    `cobertura` (0-100) se DERIVA de `cantidadComprometida / cantidadRequerida`.
    """

    id: str
    insumo: InsumoDTO
    cantidad_requerida: int = Field(alias="cantidadRequerida")
    cantidad_comprometida: int = Field(alias="cantidadComprometida")
    cantidad_recibida: int = Field(alias="cantidadRecibida")
    urgencia: str  # value del enum Urgencia (baja, media, alta)
    estado: str  # value del enum NeedStatus (activa, completada, cerrada)
    cobertura: int

    model_config = ConfigDict(populate_by_name=True)


class NeedCreateDTO(BaseModel):
    """Body de `POST /org/needs`: alta de una necesidad.

    El insumo se referencia por `insumoId` (UUID real del catálogo, NO el objeto
    anidado), y la urgencia es el enum string `alta|media|baja` (NO un booleano
    `urgente`). El centro y la cobertura/estado los resuelve el backend.
    """

    insumo_id: uuid.UUID = Field(alias="insumoId")
    cantidad_requerida: int = Field(alias="cantidadRequerida", ge=1)
    urgencia: Literal["alta", "media", "baja"]

    model_config = ConfigDict(populate_by_name=True)


class NeedUpdateDTO(BaseModel):
    """Body de `PUT /org/needs/{id}`: edición de una necesidad existente.

    Solo se editan la cantidad requerida y la urgencia; el insumo no se cambia.
    """

    cantidad_requerida: int = Field(alias="cantidadRequerida", ge=1)
    urgencia: Literal["alta", "media", "baja"]

    model_config = ConfigDict(populate_by_name=True)


class CenterTotalesDTO(BaseModel):
    """Agregados del centro: suma de sus necesidades + cobertura agregada."""

    cantidad_requerida: int = Field(alias="cantidadRequerida")
    cantidad_comprometida: int = Field(alias="cantidadComprometida")
    cantidad_recibida: int = Field(alias="cantidadRecibida")
    cobertura_general: int = Field(alias="coberturaGeneral")

    model_config = ConfigDict(populate_by_name=True)


# Texto obligatorio: recorta espacios y exige al menos un carácter no-blanco
# (un valor "   " queda vacío tras el strip y falla min_length → 422).
RequiredText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class OrgProfileDTO(BaseModel):
    """Perfil de la organización receptora autenticada (CU-09).

    Espejo de `OrgProfileDTO` del frontend. `tipo` es el value de
    `Organization.tipo_centro`; `email` viene del User-representante (no de
    `organizations`); `documentacion` es el nombre del primer documento de
    respaldo; `fechaRegistro` es `created_at` truncado a fecha (YYYY-MM-DD).
    """

    id: str
    nombre: str
    # value de TipoCentro (centro_acopio | punto_distribucion | ambos).
    tipo: str
    rut: str
    contacto_nombre: str | None = Field(alias="contactoNombre")
    email: EmailStr
    telefono: str | None
    documentacion: str
    estado: str  # value de OrganizationStatus (pendiente|activa|rechazada|inactiva)
    fecha_registro: str = Field(alias="fechaRegistro")  # ISO YYYY-MM-DD
    region: str | None
    motivo_rechazo: str | None = Field(alias="motivoRechazo")

    model_config = ConfigDict(populate_by_name=True)


class UpdateOrgProfileDTO(BaseModel):
    """Body de `PUT /org/profile`: edición de los datos de contacto (CU-09).

    Solo los 4 campos editables del mock. `contactoNombre`, `email` y `telefono`
    son obligatorios y no pueden quedar vacíos (igual que el mock); `region`
    puede ser vacío o nulo. `email` se valida con formato (EmailStr).
    """

    contacto_nombre: RequiredText = Field(alias="contactoNombre")
    email: EmailStr = Field(alias="email")
    telefono: RequiredText = Field(alias="telefono")
    region: str | None = Field(alias="region", default=None)

    model_config = ConfigDict(populate_by_name=True)


class EmergenciaRefDTO(BaseModel):
    """Referencia mínima a la emergencia a la que responde un centro (badge).

    `estado` permite a la UI distinguir un vínculo vigente (`activa`) de uno
    histórico (`cerrada`, "este centro cubrió tal evento").
    """

    id: str
    nombre: str
    estado: str  # value de EmergencyStatus (activa|cerrada)

    model_config = ConfigDict(populate_by_name=True)


class OrgCenterDTO(BaseModel):
    """Centro de acopio de la organización autenticada, con sus necesidades.

    `estado` es la SATURACIÓN derivada de la cobertura agregada
    (`en_capacidad`/`critico`/`cerrado`), no el `CenterStatus` persistido.
    `emergencia` es la emergencia a la que responde el centro (o `null`).
    """

    id: str
    nombre: str
    direccion: str
    zona: str
    horario_atencion: str | None = Field(alias="horarioAtencion")
    estado: str  # 'en_capacidad' | 'critico' | 'cerrado' (derivado)
    latitud: float | None
    longitud: float | None
    emergencia: EmergenciaRefDTO | None
    necesidades: list[NeedDTO]
    totales: CenterTotalesDTO

    model_config = ConfigDict(populate_by_name=True)


class CenterCreateDTO(BaseModel):
    """Body de `POST /org/center`: alta del centro de la organización (CU-08).

    `estado` (operatividad) nace ACTIVO y `emergency_id` queda null: ninguno se
    pide aquí. `nombre`/`direccion`/`zona` son obligatorios (no vacíos);
    `horarioAtencion` es opcional. Las coordenadas son opcionales pero deben ir
    JUNTAS (ambas o ninguna) y dentro de rango (RF-05); si no vienen, el service
    geocodifica la dirección como fallback (`org_service._resolve_center_coords`).
    """

    nombre: RequiredText
    direccion: RequiredText
    zona: RequiredText
    horario_atencion: str | None = Field(alias="horarioAtencion", default=None)
    latitud: float | None = None
    longitud: float | None = None
    # Emergencia a la que responde el centro (la elige la org). `null` = ninguna /
    # desvincular. Debe ser una emergencia ACTIVA al asignar/cambiar (validado en
    # el service); un vínculo ya existente a una cerrada se conserva como histórico.
    emergency_id: uuid.UUID | None = Field(alias="emergencyId", default=None)

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def _validar_coordenadas(self) -> "CenterCreateDTO":
        # Ambas o ninguna: una coordenada suelta no ubica nada en el mapa.
        if (self.latitud is None) != (self.longitud is None):
            raise ValueError(
                "Latitud y longitud deben enviarse juntas (ambas o ninguna)"
            )
        if self.latitud is not None:
            if not -90 <= self.latitud <= 90:
                raise ValueError("La latitud debe estar entre -90 y 90")
            if not -180 <= self.longitud <= 180:  # type: ignore[operator]
                raise ValueError("La longitud debe estar entre -180 y 180")
        return self


class CenterUpdateDTO(CenterCreateDTO):
    """Body de `PUT /org/center`: edición del centro (CU-08).

    Mismos campos editables y misma validación de coordenadas que el alta
    (`CenterCreateDTO`), **incluido `emergencyId`** (asignar/cambiar/desvincular);
    NO toca `estado` (operatividad).
    """
