"""Base declarativa y mixins compartidos por todos los modelos ORM.

SQLAlchemy 2.0: usamos `DeclarativeBase` + `Mapped`/`mapped_column` en lugar
del antiguo `declarative_base()`.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarativa única. Todo el metadata (tablas, migraciones Alembic)
    cuelga de aquí."""


class UUIDPrimaryKeyMixin:
    """PK UUID en vez de entero autoincremental.

    El frontend trata los `id` como strings (ver DTOs en el contrato); un UUID
    serializa naturalmente a string y evita exponer cardinalidad/orden de la BD.
    `Uuid` es el tipo cross-dialect nativo de SQLAlchemy 2.0 (mapea a UUID en
    PostgreSQL).
    """

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    """`created_at` / `updated_at` gestionados por la BD.

    Se usan `server_default`/`onupdate` para que el timestamp lo ponga
    PostgreSQL (consistente aunque se inserte por fuera del ORM).
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
