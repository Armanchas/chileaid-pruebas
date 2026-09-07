"""Schemas del contenido estático del landing (`statsService.ts`).

Copy fijo (hero, "cómo funciona", números de emergencia). Sin BD: el
`content_service` devuelve literales. Claves compuestas en camelCase (alias).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class HeroContentDTO(BaseModel):
    badge: str
    title: str
    subtitle: str
    primary_cta: str = Field(alias="primaryCta")
    secondary_cta: str = Field(alias="secondaryCta")

    model_config = ConfigDict(populate_by_name=True)


class HowItWorksCardDTO(BaseModel):
    id: str
    audience: str
    title: str
    description: str
    steps: list[str]
    cta: str
    accent: str  # 'navy' | 'alert'

    model_config = ConfigDict(populate_by_name=True)


class EmergencyNumberDTO(BaseModel):
    id: str
    name: str
    number: str

    model_config = ConfigDict(populate_by_name=True)


class TutorialStepDTO(BaseModel):
    """Un paso del tutorial. `icon` es una clave que el front resuelve a un SVG."""

    icon: str
    title: str
    description: str

    model_config = ConfigDict(populate_by_name=True)


class TutorialTrackDTO(BaseModel):
    """Un carril del tutorial ("cómo donar" / "cómo solicitar")."""

    id: str  # 'donante' | 'organizacion'
    audience: str
    title: str
    steps: list[TutorialStepDTO]
    cta: str
    accent: str  # 'navy' | 'alert'

    model_config = ConfigDict(populate_by_name=True)
