"""Modelo de usuario: identidad de autenticación para los tres actores.

AC-01 Donante Particular, AC-02 Organización Receptora (su representante) y
AC-03 Administrador del Sistema comparten la misma tabla de credenciales; el
`role` discrimina el acceso. Los datos institucionales de la org viven en
`Organization` (relación 1-a-1).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import UserRole

if TYPE_CHECKING:
    from .donation import Donation
    from .organization import Organization


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    # Hash (passlib/bcrypt); nunca se guarda la contraseña en claro.
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )

    # Datos personales del donante (AC-01). Nulos para org/admin.
    nombre: Mapped[str | None] = mapped_column(String(120))
    apellido: Mapped[str | None] = mapped_column(String(120))

    # --- Relaciones ---
    # Cuenta-representante de una organización (solo si role == ORG).
    organization: Mapped[Organization | None] = relationship(
        back_populates="user", uselist=False
    )
    # Aportes comprometidos por este donante (AC-01).
    donations: Mapped[list[Donation]] = relationship(back_populates="donor")
