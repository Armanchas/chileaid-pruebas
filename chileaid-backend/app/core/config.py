"""Configuración central de la app, leída del entorno con pydantic-settings.

Las variables vienen del entorno (en Docker: el bloque `environment` del
compose) o de un archivo `.env` local opcional. `settings` es la instancia
única que importa el resto del backend.
"""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 7 días: alineado con la duración de la cookie de sesión (`COOKIE_MAX_AGE` en
# `useAuth.ts`). Sin esto el token expiraba a la hora mientras la cookie
# seguía viva 7 días, dejando al usuario "logueado" en la UI pero con todo
# request devolviendo 401 (no hay refresh-token flow todavía).
_DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7


class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = _DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES

    # Base de datos
    DATABASE_URL: str

    # CORS: orígenes permitidos para el frontend. Lista separada por comas en la
    # env var (ej. "http://localhost:3000,https://app.chileaid.cl"). Se guarda
    # como string y se expone parseada en `cors_origins_list` para evitar el
    # parseo JSON que pydantic-settings aplica a los tipos lista en env vars.
    CORS_ORIGINS: str = "http://localhost:3000"

    # Geocoding (Nominatim / OpenStreetMap). Público por defecto; apuntar a una
    # instancia self-host para volumen alto. El `User-Agent` identifica la app,
    # requisito de la política de uso de Nominatim.
    NOMINATIM_URL: str = "https://nominatim.openstreetmap.org"
    NOMINATIM_USER_AGENT: str = "ChileAid/1.0 (https://chileaid.armin.moe)"

    # `.env` es opcional (en prod las vars vienen del compose); `extra=ignore`
    # evita fallar si el entorno trae otras variables no declaradas aquí.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("SECRET_KEY")
    @classmethod
    def _secret_key_no_debil(cls, v: str) -> str:
        # No hay default en el código (SECRET_KEY es obligatorio: pydantic-settings
        # ya falla el arranque si falta en el entorno); esto solo bloquea valores
        # obviamente débiles que alguien haya puesto a mano en un `.env`.
        if len(v) < 32:
            raise ValueError(
                "SECRET_KEY debe tener al menos 32 caracteres "
                "(ej. `openssl rand -hex 32`)"
            )
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
