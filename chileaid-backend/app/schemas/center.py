"""Schemas donante-facing del dominio centros/emergencias (CU-04, CU-10/CU-11).

Espejo de los DTO del frontend (`donorCentersService.ts`). Claves compuestas en
**camelCase** (alias); internamente snake_case con `populate_by_name=True`.

`cobertura` y el `estado` de saturación NO se almacenan: se DERIVAN agregando las
necesidades del centro (misma lógica que `OrgCenterDTO`). `region` se deriva de la
organización dueña (el modelo `Center` no tiene columna `region`; `zona` es la
comuna). ⚠️ Naming: SIEMPRE "cobertura", nunca "saturación".
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import EmergencyType
from app.schemas.org import NeedDTO, RequiredText


class EmergencyDTO(BaseModel):
    """Emergencia con sus agregados derivados de los centros vinculados."""

    id: str
    nombre: str
    tipo: str  # value de EmergencyType (terremoto|incendio|aluvion|otro)
    zona: str
    fecha_inicio: str = Field(alias="fechaInicio")  # ISO YYYY-MM-DD
    estado: str  # value de EmergencyStatus (activa|cerrada)
    total_centros: int = Field(alias="totalCentros")
    cobertura: int  # promedio de la cobertura de sus centros

    model_config = ConfigDict(populate_by_name=True)


class CreateEmergencyDTO(BaseModel):
    """Body de `POST /admin/emergencies` (admin). La emergencia nace `activa`.

    `tipo` se valida contra `EmergencyType`; `fechaInicio` como fecha ISO
    (`YYYY-MM-DD`, sin hora). `nombre`/`zona` no pueden ir vacíos.
    """

    nombre: RequiredText
    tipo: EmergencyType
    zona: RequiredText
    fecha_inicio: date = Field(alias="fechaInicio")

    model_config = ConfigDict(populate_by_name=True)


class CenterDTO(BaseModel):
    """Centro de acopio para el listado/mapa del donante.

    `estado` es la SATURACIÓN derivada (`critico`/`en_capacidad`/`cerrado`).
    `emergenciaId`/`tipoEmergencia` son `null` si el centro no está vinculado a
    una emergencia. `region` y `organizacion`/`tipoCentro` provienen de la org.
    """

    id: str
    nombre: str
    organizacion: str
    zona: str
    region: str | None
    cobertura: int
    estado: str  # 'critico' | 'en_capacidad' | 'cerrado' (derivado)
    emergencia_id: str | None = Field(alias="emergenciaId")
    tipo_emergencia: str | None = Field(alias="tipoEmergencia")
    # Nombre específico de la emergencia (o null): el donante lo necesita para
    # distinguir dos eventos del mismo tipo (p. ej. dos incendios simultáneos).
    emergencia_nombre: str | None = Field(alias="emergenciaNombre")
    tipo_centro: str = Field(alias="tipoCentro")
    necesidades_urgentes: list[str] = Field(alias="necesidadesUrgentes")
    direccion: str
    latitud: float | None
    longitud: float | None

    model_config = ConfigDict(populate_by_name=True)


class CenterDetailDTO(CenterDTO):
    """Detalle de un centro: extiende `CenterDTO` con datos operativos.

    `coordinador`/`telefono` provienen de la organización dueña
    (`contacto_nombre`/`telefono`); `emergencia` es el `EmergencyDTO` completo (o
    `null`); `necesidades` reutiliza el `NeedDTO` unificado (insumo anidado).
    """

    horario: str | None
    coordinador: str | None
    telefono: str | None
    emergencia: EmergencyDTO | None
    necesidades: list[NeedDTO]
