"""Seed de datos de desarrollo para ChileAid.

Pobla la BD con un set mínimo y coherente para desarrollo/demo: admin,
catálogo de insumos, organizaciones (en sus distintos estados de verificación),
donantes, una emergencia con su centro de acopio georreferenciado y necesidades.

"""

from __future__ import annotations

import os
import sys
from datetime import date

from passlib.context import CryptContext
from sqlalchemy import select

from app.db.database import SessionLocal
from app.models import (
    Center,
    CenterStatus,
    DocumentType,
    Emergency,
    EmergencyStatus,
    EmergencyType,
    Insumo,
    InsumoCategory,
    Need,
    NeedStatus,
    Organization,
    OrganizationDocument,
    OrganizationStatus,
    TipoCentro,
    Urgencia,
    User,
    UserRole,
)

# --- Hashing de passwords (bcrypt vía passlib) ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_pw(plain: str) -> str:
    return pwd_context.hash(plain)


def slug(text: str) -> str:
    """Slug simple para rutas de documentos (sin acentos ni espacios)."""
    trans = str.maketrans("áéíóúñ ", "aeioun-")
    return text.lower().translate(trans)


# --- Datos declarativos ---

ADMIN_EMAIL = "admin@chileaid.cl"

INSUMO_AGUA_EMBOTELLADA = "Agua embotellada"
REGION_BIOBIO = "Bío Bío"

# (nombre, categoria, unidad) — catálogo base de 12 insumos.
INSUMOS: list[tuple[str, InsumoCategory, str]] = [
    (INSUMO_AGUA_EMBOTELLADA, InsumoCategory.AGUA, "litros"),
    ("Alimentos no perecibles", InsumoCategory.ALIMENTOS, "kg"),
    ("Arroz", InsumoCategory.ALIMENTOS, "kg"),
    ("Frazadas", InsumoCategory.ABRIGO, "unidades"),
    ("Ropa de abrigo", InsumoCategory.ROPA, "unidades"),
    ("Kit higiene personal", InsumoCategory.HIGIENE, "unidades"),
    ("Medicamentos básicos", InsumoCategory.MEDICAMENTOS, "unidades"),
    ("Pañales", InsumoCategory.OTROS, "paquetes"),
    ("Calzado", InsumoCategory.ROPA, "pares"),
    ("Colchonetas", InsumoCategory.ABRIGO, "unidades"),
    ("Bidones de agua", InsumoCategory.AGUA, "unidades"),
    ("Conservas", InsumoCategory.ALIMENTOS, "unidades"),
]

# Cada org: cuenta-representante (role=ORG) + datos institucionales + estado.
ORGANIZACIONES: list[dict] = [
    {
        "nombre": "Cuerpo de Bomberos Los Ángeles",
        "rut": "70.120.300-K",
        "email": "bomberos.losangeles@chileaid.cl",
        "tipo_centro": TipoCentro.AMBOS,
        "direccion": "Valdivia 440, Los Ángeles, Bío Bío",
        "region": REGION_BIOBIO,
        "contacto_nombre": "Juan Pérez",
        "telefono": "+56912345678",
        "estado": OrganizationStatus.ACTIVA,
        "motivo_rechazo": None,
    },
    {
        "nombre": "Cruz Roja Angol",
        "rut": "71.234.500-2",
        "email": "cruzroja.angol@chileaid.cl",
        "tipo_centro": TipoCentro.CENTRO_ACOPIO,
        "direccion": "Gral. Oscar Bonilla 695, Angol, Araucanía",
        "region": "Araucanía",
        "contacto_nombre": "María González",
        "telefono": "+56923456789",
        "estado": OrganizationStatus.ACTIVA,
        "motivo_rechazo": None,
    },
    {
        "nombre": "Municipalidad de Temuco",
        "rut": "69.150.100-5",
        "email": "municipalidad.temuco@chileaid.cl",
        "tipo_centro": TipoCentro.PUNTO_DISTRIBUCION,
        "direccion": "Prat 650, Temuco, Araucanía",
        "region": "Araucanía",
        "contacto_nombre": "Carlos Muñoz",
        "telefono": "+56934567890",
        "estado": OrganizationStatus.ACTIVA,
        "motivo_rechazo": None,
    },
    {
        "nombre": "Municipalidad de Concepción",
        "rut": "69.264.100-7",
        "email": "municipalidad.concepcion@chileaid.cl",
        "tipo_centro": TipoCentro.AMBOS,
        "direccion": "O'Higgins 525, Concepción, Bío Bío",
        "region": REGION_BIOBIO,
        "contacto_nombre": "Felipe Araya",
        "telefono": "+56956789012",
        "estado": OrganizationStatus.ACTIVA,
        "motivo_rechazo": None,
    },
    {
        "nombre": "ONG Techo Concepción",
        "rut": "65.432.100-8",
        "email": "techo.concepcion@chileaid.cl",
        "tipo_centro": TipoCentro.AMBOS,
        "direccion": "Caupolicán 521, Concepción, Bío Bío",
        "region": REGION_BIOBIO,
        "contacto_nombre": "Ana Rojas",
        "telefono": "+56945678901",
        "estado": OrganizationStatus.RECHAZADA,
        "motivo_rechazo": "Documentación institucional incompleta",
    },
    {
        "nombre": "Fundación Refugio Sur",
        "rut": "76.318.900-1",
        "email": "refugio.sur@chileaid.cl",
        "tipo_centro": TipoCentro.CENTRO_ACOPIO,
        "direccion": "Av. Diego Portales 1450, Puerto Montt, Los Lagos",
        "region": "Los Lagos",
        "contacto_nombre": "Rosa Maldonado",
        "telefono": "+56967890123",
        "estado": OrganizationStatus.PENDIENTE,
        "motivo_rechazo": None,
    },
]

# (nombre, apellido, email)
DONANTES: list[tuple[str, str, str]] = [
    ("Pedro", "Soto", "pedro.soto@gmail.com"),
    ("Valentina", "Mora", "valentina.mora@gmail.com"),
    ("Diego", "Fuentes", "diego.fuentes@gmail.com"),
]

# (key, nombre, tipo, zona, fecha_inicio) — emergencias activas. La `key` enlaza
# cada centro con su emergencia (ver CENTROS); dos eventos en regiones distintas.
EMERGENCIAS: list[tuple[str, str, EmergencyType, str, date]] = [
    ("biobio_incendio", "Incendio Forestal Bío Bío 2026", EmergencyType.INCENDIO, REGION_BIOBIO, date(2026, 1, 15)),
    ("araucania_terremoto", "Terremoto La Araucanía 2026", EmergencyType.TERREMOTO, "La Araucanía", date(2026, 5, 18)),
]

# Un centro por cada org ACTIVA. Cada `needs` = (insumo, requerida, comprometida,
# recibida, urgencia) con `comprometida <= requerida` (invariante no-sobrestock).
# Cobertura agregada DISTINTA por centro para ejercitar la saturación (RF-07):
#   - Angol: ~92% (saturado/casi cerrado, con una need al 95%)
#   - Temuco: ~47% (en capacidad)
#   - Concepción: 0% (crítico real, RF-07) y SIN emergencia asociada (emergency_key=None)
#   - Bomberos: ~35% (en capacidad), el centro original
CENTROS: list[dict] = [
    {
        "org": "Cuerpo de Bomberos Los Ángeles",
        "nombre": "Centro de Acopio Bomberos Los Ángeles",
        "emergency_key": "biobio_incendio",
        "zona": "Los Ángeles",
        "direccion": "Valdivia 440, Los Ángeles, Bío Bío",
        "horario_atencion": "Lunes a Domingo 08:00 - 20:00",
        "latitud": -37.4697,
        "longitud": -72.3522,
        "needs": [
            (INSUMO_AGUA_EMBOTELLADA, 500, 200, 0, Urgencia.ALTA),
            ("Frazadas", 100, 30, 0, Urgencia.MEDIA),
            ("Arroz", 50, 0, 0, Urgencia.BAJA),
        ],
    },
    {
        "org": "Cruz Roja Angol",
        "nombre": "Centro de Acopio Cruz Roja Angol",
        "emergency_key": "araucania_terremoto",
        "zona": "Angol",
        "direccion": "Gral. Oscar Bonilla 695, Angol, Araucanía",
        "horario_atencion": "Lunes a Viernes 09:00 - 18:00",
        "latitud": -37.7975,
        "longitud": -72.7164,
        "needs": [
            (INSUMO_AGUA_EMBOTELLADA, 200, 190, 0, Urgencia.ALTA),   # 95% (casi al tope)
            ("Frazadas", 100, 88, 0, Urgencia.MEDIA),           # 88%
            ("Medicamentos básicos", 50, 45, 0, Urgencia.ALTA),  # 90%
        ],
    },
    {
        "org": "Municipalidad de Temuco",
        "nombre": "Punto de Distribución Municipalidad de Temuco",
        "emergency_key": "araucania_terremoto",
        "zona": "Temuco",
        "direccion": "Prat 650, Temuco, Araucanía",
        "horario_atencion": "Lunes a Sábado 08:30 - 19:00",
        "latitud": -38.7359,
        "longitud": -72.5904,
        "needs": [
            ("Arroz", 300, 150, 0, Urgencia.MEDIA),             # 50%
            ("Kit higiene personal", 200, 90, 0, Urgencia.BAJA),  # 45%
            ("Colchonetas", 80, 40, 0, Urgencia.ALTA),          # 50%
            ("Conservas", 120, 48, 0, Urgencia.MEDIA),          # 40%
        ],
    },
    {
        "org": "Municipalidad de Concepción",
        "nombre": "Centro de Acopio Municipalidad de Concepción",
        "emergency_key": None,  # centro sin emergencia asociada (caso a cubrir)
        "zona": "Concepción",
        "direccion": "O'Higgins 525, Concepción, Bío Bío",
        "horario_atencion": "Todos los días 09:00 - 21:00",
        "latitud": -36.8270,
        "longitud": -73.0498,
        "needs": [
            ("Pañales", 150, 0, 0, Urgencia.ALTA),              # 0% (sin aportes aún)
            ("Calzado", 100, 0, 0, Urgencia.MEDIA),             # 0%
            ("Bidones de agua", 200, 0, 0, Urgencia.ALTA),      # 0%
        ],
    },
]


def get_seed_password() -> str:
    """Contraseña común de las cuentas del seed, leída de SEED_DEFAULT_PASSWORD.

    No hay valor por defecto: si la variable falta o está vacía, el seed aborta.
    """
    password = os.getenv("SEED_DEFAULT_PASSWORD")
    if not password:
        sys.exit(
            "✗ Falta la variable de entorno SEED_DEFAULT_PASSWORD. "
            "Defínela (ver .env.ejemplo) antes de correr el seed."
        )
    return password


def seed() -> None:
    seed_password = get_seed_password()
    # Requiere que las migraciones ya estén aplicadas (`alembic upgrade head`,
    # §2.4). El servicio `seed` de docker-compose lo hace antes de llamar a
    # este script; en dev local corré `alembic upgrade head` antes de `python seed.py`.
    db = SessionLocal()
    try:
        # --- Idempotencia: si el admin ya existe, no hacemos nada ---
        if db.scalar(select(User).where(User.email == ADMIN_EMAIL)):
            print("• El seed ya fue aplicado (admin existe). Nada que insertar.")
            return

        # 1) ADMIN
        db.add(User(
            email=ADMIN_EMAIL,
            password_hash=hash_pw(seed_password),
            role=UserRole.ADMIN,
        ))
        db.flush()
        print("✓ Admin creado")

        # 2) INSUMOS (catálogo base)
        insumos_by_name: dict[str, Insumo] = {}
        for nombre, categoria, unidad in INSUMOS:
            insumo = Insumo(nombre=nombre, categoria=categoria, unidad=unidad)
            db.add(insumo)
            insumos_by_name[nombre] = insumo
        db.flush()
        print(f"✓ {len(INSUMOS)} insumos insertados")

        # 3) ORGANIZACIONES (+ su User role=ORG) y 8) sus DOCUMENTOS
        orgs_by_name: dict[str, Organization] = {}
        for data in ORGANIZACIONES:
            user = User(
                email=data["email"],
                password_hash=hash_pw(seed_password),
                role=UserRole.ORG,
            )
            db.add(user)
            db.flush()  # asigna user.id para el FK de la organización

            org = Organization(
                user_id=user.id,
                nombre=data["nombre"],
                rut=data["rut"],
                tipo_centro=data["tipo_centro"],
                direccion=data["direccion"],
                region=data["region"],
                contacto_nombre=data["contacto_nombre"],
                telefono=data["telefono"],
                estado=data["estado"],
                motivo_rechazo=data["motivo_rechazo"],
            )
            db.add(org)
            db.flush()  # asigna org.id para el FK del documento

            db.add(OrganizationDocument(
                organization_id=org.id,
                nombre_archivo="registro.pdf",
                ruta=f"/docs/seed/{slug(data['nombre'])}/registro.pdf",
                tipo=DocumentType.PDF,
            ))
            orgs_by_name[data["nombre"]] = org
        db.flush()
        print(f"✓ {len(ORGANIZACIONES)} organizaciones insertadas (con su usuario y documento)")

        # 4) DONANTES
        for nombre, apellido, email in DONANTES:
            db.add(User(
                email=email,
                password_hash=hash_pw(seed_password),
                role=UserRole.DONOR,
                nombre=nombre,
                apellido=apellido,
            ))
        db.flush()
        print(f"✓ {len(DONANTES)} donantes insertados")

        # 5) EMERGENCIAS (dos activas, en regiones distintas)
        emergencias_by_key: dict[str, Emergency] = {}
        for key, nombre, tipo, zona, fi in EMERGENCIAS:
            em = Emergency(
                nombre=nombre, tipo=tipo, zona=zona, fecha_inicio=fi,
                estado=EmergencyStatus.ACTIVA,
            )
            db.add(em)
            emergencias_by_key[key] = em
        db.flush()
        print(f"✓ {len(EMERGENCIAS)} emergencias creadas")

        # 6+7) CENTROS (uno por org activa) + sus NECESIDADES. Coordenadas
        #      hardcodeadas; en producción las resuelve el GeoService desde la
        #      dirección. `emergency_key=None` deja el centro sin emergencia
        #      asociada (caso a cubrir en CenterDetailDTO.emergencia).
        centros_creados: list[Center] = []
        for c in CENTROS:
            emergency_id = (
                emergencias_by_key[c["emergency_key"]].id
                if c["emergency_key"] is not None
                else None
            )
            centro = Center(
                nombre=c["nombre"],
                organization_id=orgs_by_name[c["org"]].id,
                emergency_id=emergency_id,
                zona=c["zona"],
                direccion=c["direccion"],
                horario_atencion=c["horario_atencion"],
                estado=CenterStatus.ACTIVO,
                latitud=c["latitud"],
                longitud=c["longitud"],
            )
            db.add(centro)
            db.flush()  # asigna centro.id para el FK de las necesidades

            for insumo_nombre, req, comp, recib, urgencia in c["needs"]:
                # Invariante de no-sobrestock (ck_need_no_sobrestock): comp <= req.
                assert comp <= req, f"{c['nombre']}/{insumo_nombre}: comp>req"
                db.add(Need(
                    center_id=centro.id,
                    insumo_id=insumos_by_name[insumo_nombre].id,
                    cantidad_requerida=req,
                    cantidad_comprometida=comp,
                    cantidad_recibida=recib,
                    urgencia=urgencia,
                    estado=NeedStatus.ACTIVA,
                ))
            centros_creados.append(centro)
        db.flush()
        total_needs = sum(len(c["needs"]) for c in CENTROS)
        print(f"✓ {len(CENTROS)} centros y {total_needs} necesidades insertados")

        db.commit()
        print("✓ Seed completado correctamente")

        # Referencia para pruebas E2E manuales: id (UUID) de cada centro.
        print("\nCentros (id · nombre · emergencia):")
        for c, centro in zip(CENTROS, centros_creados):
            emergencia_lbl = c["emergency_key"] or "—(sin emergencia)"
            print(f"  {centro.id}  {centro.nombre}  [{emergencia_lbl}]")

    except Exception as exc:  # rollback total ante cualquier fallo
        db.rollback()
        print(f"✗ Error durante el seed, se revirtió todo: {exc}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
