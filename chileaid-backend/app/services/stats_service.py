"""Agregados de la plataforma: landing público (`/stats`) y dashboard admin
(`/admin/stats`). Todo `COUNT`/`SUM` server-side, derivado (no persistido).

Regla base de donaciones: se **excluyen las canceladas** (`DonationStatus.CANCELADA`)
tanto en el conteo de aportes como en el de donantes activos.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.models import (
    Center,
    CenterStatus,
    DistributionLot,
    Donation,
    DonationStatus,
    Emergency,
    EmergencyStatus,
    Organization,
    OrganizationStatus,
)
from app.schemas.stats import PlatformStatsDTO, StatItemDTO


def _count(db: Session, stmt) -> int:
    return int(db.scalar(stmt) or 0)


def get_public_stats(db: Session) -> list[StatItemDTO]:
    """4 métricas del landing público (sin "familias beneficiadas", retirada).

    Donantes activos = donantes DISTINTOS con al menos un aporte NO cancelado;
    aportes registrados = donaciones no canceladas.
    """
    centros = _count(
        db,
        select(func.count()).select_from(Center).where(Center.estado == CenterStatus.ACTIVO),
    )
    donantes = _count(
        db,
        select(func.count(distinct(Donation.donor_id))).where(
            Donation.estado != DonationStatus.CANCELADA
        ),
    )
    aportes = _count(
        db,
        select(func.count())
        .select_from(Donation)
        .where(Donation.estado != DonationStatus.CANCELADA),
    )
    emergencias = _count(
        db,
        select(func.count())
        .select_from(Emergency)
        .where(Emergency.estado == EmergencyStatus.ACTIVA),
    )
    return [
        StatItemDTO(id="centros", value=centros, label="Centros operativos"),
        StatItemDTO(id="donantes", value=donantes, label="Donantes activos"),
        StatItemDTO(id="aportes", value=aportes, label="Aportes registrados"),
        StatItemDTO(id="emergencias", value=emergencias, label="Emergencias activas"),
    ]


def get_platform_stats(db: Session) -> PlatformStatsDTO:
    """Métricas globales del dashboard admin.

    `donacionesTotales`/`donacionesUltimos7Dias` excluyen canceladas.
    `entregasRealizadas` = `COUNT` de lotes de distribución (cada salida cuenta 1);
    se prefiere sobre `SUM(cantidad)` para NO mezclar unidades de medida
    heterogéneas (kg/litros/unidades) en un total sin sentido físico.
    """
    hace_7_dias = datetime.now(timezone.utc) - timedelta(days=7)
    no_cancelada = Donation.estado != DonationStatus.CANCELADA
    return PlatformStatsDTO(
        organizaciones_activas=_count(
            db,
            select(func.count())
            .select_from(Organization)
            .where(Organization.estado == OrganizationStatus.ACTIVA),
        ),
        organizaciones_pendientes=_count(
            db,
            select(func.count())
            .select_from(Organization)
            .where(Organization.estado == OrganizationStatus.PENDIENTE),
        ),
        donaciones_totales=_count(
            db, select(func.count()).select_from(Donation).where(no_cancelada)
        ),
        donaciones_ultimos_7_dias=_count(
            db,
            select(func.count())
            .select_from(Donation)
            .where(no_cancelada, Donation.created_at >= hace_7_dias),
        ),
        emergencias_activas=_count(
            db,
            select(func.count())
            .select_from(Emergency)
            .where(Emergency.estado == EmergencyStatus.ACTIVA),
        ),
        centros_operativos=_count(
            db,
            select(func.count())
            .select_from(Center)
            .where(Center.estado == CenterStatus.ACTIVO),
        ),
        entregas_realizadas=_count(
            db, select(func.count()).select_from(DistributionLot)
        ),
    )
