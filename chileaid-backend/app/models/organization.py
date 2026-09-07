"""Organización receptora (AC-02) y sus documentos de respaldo (RF-03).

El registro (CU-01) crea la organización en estado PENDIENTE junto a los
documentos oficiales; la validación del admin (CU-02) cambia el estado.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import DocumentType, OrganizationStatus, TipoCentro

if TYPE_CHECKING:
    from .center import Center
    from .user import User


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "organizations"

    # Cuenta de login asociada (representante). 1-a-1 con un User role=ORG.
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    # RUT institucional chileno, único para evitar registros duplicados (CU-01).
    # Opcional en el registro: si se informa debe ser único; varios NULL conviven
    # (en Postgres/SQLite los NULL no colisionan bajo UNIQUE).
    rut: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    # Función del centro (acopio / distribución / ambos). Espejo de `OrgType`
    # del frontend; editable como solo-lectura en el perfil (CU-09).
    tipo_centro: Mapped[TipoCentro] = mapped_column(
        SAEnum(
            TipoCentro,
            name="tipo_centro",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=TipoCentro.CENTRO_ACOPIO,
        nullable=False,
    )
    direccion: Mapped[str | None] = mapped_column(String(300))
    region: Mapped[str | None] = mapped_column(String(120))

    # Datos de contacto (editables en CU-09 / perfil de org).
    contacto_nombre: Mapped[str | None] = mapped_column(String(200))
    telefono: Mapped[str | None] = mapped_column(String(30))

    estado: Mapped[OrganizationStatus] = mapped_column(
        SAEnum(
            OrganizationStatus,
            name="organization_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        default=OrganizationStatus.PENDIENTE,
        nullable=False,
    )
    # Motivo cuando el admin rechaza (CU-02, flujo alternativo 4a).
    motivo_rechazo: Mapped[str | None] = mapped_column(Text)

    # --- Relaciones ---
    user: Mapped[User] = relationship(back_populates="organization")
    documents: Mapped[list[OrganizationDocument]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    centers: Mapped[list[Center]] = relationship(back_populates="organization")


class OrganizationDocument(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Documento oficial de respaldo subido en el registro (RF-03, CU-01).

    Solo se guarda la referencia al archivo (ruta/URL), no el binario.
    """

    __tablename__ = "organization_documents"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    nombre_archivo: Mapped[str] = mapped_column(String(255), nullable=False)
    # Ruta/URL al storage; el formato permitido es PDF o JPG (CU-01, 3a).
    ruta: Mapped[str] = mapped_column(String(500), nullable=False)
    tipo: Mapped[DocumentType] = mapped_column(
        SAEnum(DocumentType, name="document_type", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )

    organization: Mapped[Organization] = relationship(back_populates="documents")
