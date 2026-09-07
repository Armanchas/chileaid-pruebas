"""Configuración de la base de datos (SQLAlchemy 2.0, síncrono).

MVP sobre PostgreSQL en Docker. La URL llega por la variable de entorno
`DATABASE_URL` (definida en docker-compose para el servicio `backend`):

    postgresql://<user>:<password>@db:5432/<db>

Driver: psycopg2 (síncrono), ya presente en requirements.txt.
"""

from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.environ["DATABASE_URL"]  # falla rápido y claro si no está seteada

# pool_pre_ping: emite un ping antes de prestar cada conexión del pool y la
# recicla si está muerta. Clave en Docker, donde el contenedor `db` puede
# reiniciarse y dejar conexiones colgadas en el pool del backend.
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)

# autoflush=False: no se hace flush implícito antes de cada query (control
# explícito). autocommit no se pasa: en SQLAlchemy 2.0 fue eliminado y la
# sesión ya es siempre transaccional (autocommit=False por diseño).
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    """Dependency de FastAPI: abre una sesión por request y la cierra al final.

    Uso:  def endpoint(db: Session = Depends(get_db)): ...
    El commit/rollback es responsabilidad del service/endpoint; aquí solo se
    garantiza el cierre de la sesión.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
