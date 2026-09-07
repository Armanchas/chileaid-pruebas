"""Router del contenido estático del landing (público, sin token).

Copy fijo servido desde el backend (hero, "cómo funciona", números de emergencia).
No depende de la BD; los literales viven en `content_service`.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.content import (
    EmergencyNumberDTO,
    HeroContentDTO,
    HowItWorksCardDTO,
    TutorialTrackDTO,
)
from app.services import content_service

router = APIRouter(prefix="/content", tags=["content"])


@router.get("/hero", response_model=HeroContentDTO)
def get_hero() -> HeroContentDTO:
    """Contenido del hero del landing."""
    return content_service.get_hero()


@router.get("/how-it-works", response_model=list[HowItWorksCardDTO])
def get_how_it_works() -> list[HowItWorksCardDTO]:
    """Tarjetas de la sección "Cómo funciona"."""
    return content_service.get_how_it_works()


@router.get("/tutorial", response_model=list[TutorialTrackDTO])
def get_tutorial() -> list[TutorialTrackDTO]:
    """Tutorial visual: cómo donar (donante) y cómo solicitar (organización)."""
    return content_service.get_tutorial()


@router.get("/emergency-numbers", response_model=list[EmergencyNumberDTO])
def get_emergency_numbers() -> list[EmergencyNumberDTO]:
    """Números de emergencia oficiales (131/132/133)."""
    return content_service.get_emergency_numbers()
