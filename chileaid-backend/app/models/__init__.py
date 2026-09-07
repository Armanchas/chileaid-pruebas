"""Modelos ORM de Chile Aid.

Importa todos los modelos para que queden registrados en `Base.metadata`
(Alembic / `create_all`). Importar desde aquí: `from app.models import User`.
"""

from .activity import ActivityLog
from .base import Base
from .catalog import Insumo
from .center import Center
from .distribution import DistributionLot
from .donation import Donation, DonationItem
from .emergency import Emergency
from .enums import (
    ActivityType,
    CenterStatus,
    DocumentType,
    DonationStatus,
    EmergencyStatus,
    EmergencyType,
    InsumoCategory,
    LotSalida,
    MotivoCancelacion,
    NeedStatus,
    OrganizationStatus,
    TipoCentro,
    Urgencia,
    UserRole,
)
from .need import Need
from .organization import Organization, OrganizationDocument
from .user import User

__all__ = [
    "Base",
    # Modelos
    "User",
    "Organization",
    "OrganizationDocument",
    "Emergency",
    "Center",
    "Insumo",
    "Need",
    "Donation",
    "DonationItem",
    "DistributionLot",
    "ActivityLog",
    # Enums
    "UserRole",
    "OrganizationStatus",
    "TipoCentro",
    "DocumentType",
    "EmergencyType",
    "EmergencyStatus",
    "CenterStatus",
    "InsumoCategory",
    "LotSalida",
    "ActivityType",
    "Urgencia",
    "NeedStatus",
    "DonationStatus",
    "MotivoCancelacion",
]
