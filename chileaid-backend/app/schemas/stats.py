"""Schemas de estadísticas/agregados (landing público + dashboard admin).

Espejo de `statsService.ts` (`StatItem`) y `adminDashboardService.ts`
(`PlatformStatsDTO`, `RecentActivityItem`). El backend devuelve el `value` crudo y
el `label`; el `display` ("45K+") lo formatea el frontend (presentación).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class StatItemDTO(BaseModel):
    """Métrica pública del landing: valor crudo + etiqueta (el `display` lo formatea
    el frontend)."""

    id: str
    value: int
    label: str

    model_config = ConfigDict(populate_by_name=True)


class PlatformStatsDTO(BaseModel):
    """Métricas globales del dashboard admin (todos `COUNT`/`SUM` server-side)."""

    organizaciones_activas: int = Field(alias="organizacionesActivas")
    organizaciones_pendientes: int = Field(alias="organizacionesPendientes")
    donaciones_totales: int = Field(alias="donacionesTotales")
    donaciones_ultimos_7_dias: int = Field(alias="donacionesUltimos7Dias")
    emergencias_activas: int = Field(alias="emergenciasActivas")
    centros_operativos: int = Field(alias="centrosOperativos")
    # Nº de salidas de distribución (COUNT de lotes), no suma de cantidades: no se
    # mezclan unidades de medida heterogéneas (kg/litros/unidades).
    entregas_realizadas: int = Field(alias="entregasRealizadas")

    model_config = ConfigDict(populate_by_name=True)


class RecentActivityItemDTO(BaseModel):
    """Evento del feed de actividad del admin (solo ciclo de vida de orgs)."""

    id: str
    tipo: str  # value de ActivityType (org_registrada|org_aprobada|org_rechazada)
    descripcion: str
    fecha: str  # ISO YYYY-MM-DD

    model_config = ConfigDict(populate_by_name=True)
