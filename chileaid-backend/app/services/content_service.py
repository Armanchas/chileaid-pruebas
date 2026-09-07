"""Contenido estático del landing (CU-index). Sin BD: literales fijos.

Reemplaza los mocks de contenido de `statsService.ts` (hero, "cómo funciona",
números de emergencia). Se sirve desde el backend por consistencia arquitectónica
(todo el contenido del cliente sale de la API), aunque no dependa de la BD.
"""

from __future__ import annotations

from app.schemas.content import (
    EmergencyNumberDTO,
    HeroContentDTO,
    HowItWorksCardDTO,
    TutorialStepDTO,
    TutorialTrackDTO,
)


def get_hero() -> HeroContentDTO:
    return HeroContentDTO(
        badge="Respuesta de Emergencia Activa",
        title="Coordinando la ayuda donde más se necesita",
        subtitle=(
            "Conectamos a la ciudadanía con organizaciones receptoras verificadas, "
            "mostrando las necesidades reales de cada zona afectada en tiempo real."
        ),
        primary_cta="Donar Ahora",
        secondary_cta="Registrar Centro de Acopio",
    )


def get_how_it_works() -> list[HowItWorksCardDTO]:
    return [
        HowItWorksCardDTO(
            id="ciudadanos",
            audience="Para Ciudadanos",
            title="Dona con certeza",
            description=(
                "Encuentra qué se necesita realmente, dónde entregarlo y a quién "
                "ayuda tu aporte."
            ),
            steps=[
                "Revisa las necesidades verificadas de tu región",
                "Elige un centro de acopio cercano y autorizado",
                "Entrega tu donación y sigue su impacto",
            ],
            cta="Quiero donar",
            accent="alert",
        ),
        HowItWorksCardDTO(
            id="organizaciones",
            audience="Para Organizaciones",
            title="Coordina la recepción",
            description=(
                "Publica tus necesidades, gestiona tu inventario y evita la "
                "saturación de recursos."
            ),
            steps=[
                "Verifica tu organización ante la plataforma",
                "Publica necesidades específicas y prioridades",
                "Administra el flujo de donaciones en tiempo real",
            ],
            cta="Registrar organización",
            accent="navy",
        ),
    ]


def get_tutorial() -> list[TutorialTrackDTO]:
    """Tutorial visual paso a paso: cómo donar (donante) y cómo solicitar (org).

    Dos carriles con el flujo real de la plataforma. `icon` es una clave que el
    front resuelve a un SVG inline (presentación); el copy vive aquí.
    """
    return [
        TutorialTrackDTO(
            id="donante",
            audience="Quiero ayudar",
            title="Cómo donar",
            steps=[
                TutorialStepDTO(
                    icon="search",
                    title="Revisa las necesidades",
                    description=(
                        "Explora en el mapa qué se necesita realmente en cada "
                        "zona afectada, verificado por organizaciones."
                    ),
                ),
                TutorialStepDTO(
                    icon="pin",
                    title="Elige un centro",
                    description=(
                        "Selecciona un centro de acopio activo y cercano según "
                        "lo que puedas aportar."
                    ),
                ),
                TutorialStepDTO(
                    icon="gift",
                    title="Haz tu donación",
                    description=(
                        "Registra tu aporte a las necesidades del centro y recibe "
                        "un código de seguimiento."
                    ),
                ),
                TutorialStepDTO(
                    icon="route",
                    title="Sigue su impacto",
                    description=(
                        "Acompaña tu donación hasta que el centro confirma la "
                        "recepción."
                    ),
                ),
            ],
            cta="Quiero donar",
            accent="alert",
        ),
        TutorialTrackDTO(
            id="organizacion",
            audience="Soy una organización",
            title="Cómo solicitar",
            steps=[
                TutorialStepDTO(
                    icon="shield",
                    title="Verifica tu organización",
                    description=(
                        "Regístrate y valida tu organización ante la plataforma "
                        "para operar como centro de acopio."
                    ),
                ),
                TutorialStepDTO(
                    icon="clipboard",
                    title="Publica tus necesidades",
                    description=(
                        "Detalla qué insumos necesitas y con qué prioridad, "
                        "actualizados en tiempo real."
                    ),
                ),
                TutorialStepDTO(
                    icon="inbox",
                    title="Recibe y confirma",
                    description=(
                        "Gestiona el flujo de donaciones y confirma cada "
                        "recepción cuando llega al centro."
                    ),
                ),
            ],
            cta="Registrar organización",
            accent="navy",
        ),
    ]


def get_emergency_numbers() -> list[EmergencyNumberDTO]:
    return [
        EmergencyNumberDTO(id="samu", name="SAMU — Ambulancias", number="131"),
        EmergencyNumberDTO(id="bomberos", name="Bomberos", number="132"),
        EmergencyNumberDTO(id="carabineros", name="Carabineros", number="133"),
    ]
