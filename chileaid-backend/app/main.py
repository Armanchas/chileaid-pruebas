from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.limiter import limiter
from app.routers import (
    admin,
    auth,
    center,
    content,
    donation,
    donor,
    emergency,
    geocode,
    org,
    stats,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # El esquema lo aplican las migraciones de Alembic (§2.4), no el arranque
    # de la app: `alembic upgrade head` corre antes de `uvicorn` (Dockerfile
    # CMD) o a mano en dev (`alembic upgrade head`).
    yield
    # Apagado: nada que limpiar por ahora.


app = FastAPI(lifespan=lifespan)

# Rate limiting (§2.3): estado del limiter + handler del 429 para los endpoints
# que lo usan (hoy solo POST /auth/login, ver routers/auth.py).
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS: el navegador envía un preflight OPTIONS antes de los POST con cuerpo
# JSON; sin este middleware el backend responde 405 y faltan las cabeceras
# Access-Control-Allow-*. El frontend manda el token vía header Authorization
# (no cookies), por eso allow_credentials queda en False.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(org.router)
app.include_router(donation.router)
app.include_router(donor.router)
app.include_router(center.router)
app.include_router(emergency.router)
app.include_router(content.router)
app.include_router(stats.router)
app.include_router(geocode.router)


@app.get("/")
def read_root():
    return {"message": "Backend is running"}
