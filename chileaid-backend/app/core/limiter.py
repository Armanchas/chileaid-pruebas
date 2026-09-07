"""Rate limiting (§2.3): protege `POST /auth/login` de fuerza bruta/enumeración.

Instancia única de `Limiter`, keyeada por IP del cliente. Se registra en
`main.py` (exception handler del 429) y se aplica por endpoint con
`@limiter.limit(...)` donde haga falta.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
