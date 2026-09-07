"""ENUMs del dominio (Python Enum + SQLAlchemy Enum).

Cada `Enum` de Python se materializa como tipo ENUM nativo de PostgreSQL al
declararse en una columna con `SAEnum(...)`. Por convención usamos
`values_callable=lambda e: [m.value for m in e]` en las columnas para que en la
BD se almacene el *value* (string en español del contrato) y no el *name*.

⚠️ Los valores string deben calzar EXACTAMENTE con las uniones TypeScript del
frontend (contrato de datos). Un valor extra rompe el tipado del cliente.
"""

from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    """Rol que decide el acceso (resuelto desde el JWT).

    Mapea a los actores: DONOR=AC-01, ORG=AC-02 (representante), ADMIN=AC-03.
    """

    DONOR = "donor"
    ORG = "org"
    ADMIN = "admin"


class OrganizationStatus(str, enum.Enum):
    """Estado de verificación de una organización receptora (RF-03, CU-02).

    Nace `PENDIENTE`; el admin la mueve a `ACTIVA`/`RECHAZADA`, y puede
    desactivar/reactivar (`INACTIVA`).
    """

    PENDIENTE = "pendiente"
    ACTIVA = "activa"
    RECHAZADA = "rechazada"
    INACTIVA = "inactiva"


class TipoCentro(str, enum.Enum):
    """Función del centro de la organización dentro de la red de ayuda (CU-09).

    Espejo de la unión `OrgType` del frontend (`orgProfileService.ts`):
    acopia donaciones, las distribuye, o ambas cosas.
    """

    CENTRO_ACOPIO = "centro_acopio"
    PUNTO_DISTRIBUCION = "punto_distribucion"
    AMBOS = "ambos"


class DocumentType(str, enum.Enum):
    """Formato del documento de respaldo subido al registrar la org (CU-01)."""

    PDF = "pdf"
    JPG = "jpg"


class EmergencyType(str, enum.Enum):
    """Tipo de catástrofe que agrupa centros de acopio."""

    TERREMOTO = "terremoto"
    INCENDIO = "incendio"
    ALUVION = "aluvion"
    OTRO = "otro"


class EmergencyStatus(str, enum.Enum):
    ACTIVA = "activa"
    CERRADA = "cerrada"


class CenterStatus(str, enum.Enum):
    """Estado de OPERATIVIDAD del centro (persistido).

    `ACTIVO`: el centro opera y recibe donaciones.
    `CERRADO`: el centro ya no recibe.

    ⚠️ No confundir con la SATURACIÓN visual del mapa (RF-07,
    'en_capacidad'/'critico'/'cerrado'): esa NO se persiste, se deriva de la
    cobertura de las necesidades del centro en el service y se entrega en el
    `estado` del CenterDTO al frontend.
    """

    ACTIVO = "activo"
    CERRADO = "cerrado"


class InsumoCategory(str, enum.Enum):
    """Categoría de insumo. Alimenta el filtro de marcadores del mapa (RF-06)."""

    AGUA = "agua"
    ALIMENTOS = "alimentos"
    ROPA = "ropa"
    ABRIGO = "abrigo"
    HIGIENE = "higiene"
    MEDICAMENTOS = "medicamentos"
    OTROS = "otros"


class Urgencia(str, enum.Enum):
    """Nivel de urgencia de una necesidad (CU-03 / filtro CU-04).

    El frontend expone un booleano `urgente`; se considera urgente cuando la
    necesidad es ALTA. Modelar el nivel completo da más expresividad sin romper
    ese mapeo.
    """

    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class NeedStatus(str, enum.Enum):
    """Estado de la solicitud de insumo (CU-03).

    `COMPLETADA`: la meta llegó al 100% (cierre automático, RF-04).
    `CERRADA`: cierre manual por la organización.
    """

    ACTIVA = "activa"
    COMPLETADA = "completada"
    CERRADA = "cerrada"


class DonationStatus(str, enum.Enum):
    """Estado del aporte comprometido (CU-06).

    `PENDIENTE`: comprometido (reserva cupo en la barra de progreso), aún no
    entregado/confirmado.
    `RECIBIDO`: confirmado físicamente en el centro vía escaneo de código (CU-07).
    `CANCELADA`: el aporte se anuló (soft-cancel). La donación llega aquí solo
    cuando TODOS sus ítems quedan cancelados (ver `DonationItem.activo`); si
    sobrevive al menos un ítem activo, sigue `PENDIENTE`. Un `RECIBIDO` nunca se
    cancela.
    """

    PENDIENTE = "pendiente"
    RECIBIDO = "recibido"
    CANCELADA = "cancelada"


class ActivityType(str, enum.Enum):
    """Tipo de evento del feed de actividad del admin (dashboard).

    Solo eventos del ciclo de vida de organizaciones (el admin monitorea el alta y
    la moderación de orgs, no donaciones ni emergencias).
    """

    ORG_REGISTRADA = "org_registrada"
    ORG_APROBADA = "org_aprobada"
    ORG_RECHAZADA = "org_rechazada"


class LotSalida(str, enum.Enum):
    """Acción de salida de un lote de distribución (CU-08).

    `ENVIADO_A_TERRENO`: el centro de acopio despacha insumos a terreno.
    `ENTREGADO_A_BENEFICIARIO`: el punto de distribución entrega a una persona.
    El tipo de salida permitido depende del `tipo_centro` de la organización
    (acopio → terreno; distribución → beneficiario; ambos → los dos).
    """

    ENVIADO_A_TERRENO = "enviado_a_terreno"
    ENTREGADO_A_BENEFICIARIO = "entregado_a_beneficiario"


class MotivoCancelacion(str, enum.Enum):
    """Por qué se canceló un `DonationItem` (soft-cancel). Alimenta el mensaje del
    tracking según quién disparó la cancelación.

    `DONANTE`: el donante anuló su propio aporte pendiente
    (`POST /donations/{id}/cancel`).
    `CIERRE_NECESIDAD`: la organización cerró manualmente la necesidad
    (`PATCH /org/needs/{id}/cerrar`) y los aportes pendientes que la referenciaban
    ya no se recibirán.
    """

    DONANTE = "donante"
    CIERRE_NECESIDAD = "cierre_necesidad"
