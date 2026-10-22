# Resultados SonarQube tras las correcciones — ChileAid

Re-análisis con el mismo comando Docker (http://localhost:9100/dashboard?id=chileaid).

## Antes / después

| Métrica | Antes | Después | Fuente del "después" |
|---|---|---|---|
| Bugs | 1 | **0** | API `issues/search` |
| Vulnerabilities | 0 | **0** | API `issues/search` |
| Code Smells | 14 | **4** (2 MAJOR, 2 INFO) | API `issues/search` |
| Security Hotspots | 6 | *no disponible por API* | ver nota |
| Coverage | 0.0% | *no disponible por API* (sin tests, sigue en 0%) | ver nota |
| Duplications % | 0.0% | *no disponible por API*; en la condición del gate `new_duplicated_lines_density` = 0.0% | gate |
| Maintainability Rating | A | *no disponible por API*; `new_maintainability_rating` = A (1) | gate |
| Security Rating | A | *no disponible por API*; `new_security_rating` = A (1) | gate |
| Reliability Rating | B | *no disponible por API*; `new_reliability_rating` = A (1) | gate |
| Security Review Rating | E | *no disponible por API* | ver nota |
| Quality Gate | Passed | **ERROR (Failed)** | API `qualitygates/project_status` |

> **Nota — datos faltantes:** el token `sqp_...` es de análisis de proyecto y `/api/measures/*` y
> `/api/hotspots/search` responden `Insufficient privileges`. Los valores marcados se leen en el
> dashboard o con un token de usuario. Los ratings `new_*` corresponden solo al código nuevo
> (desde el análisis anterior), no a todo el proyecto. Los Hotspots y el Security Review Rating
> deberían mejorar al quitar las contraseñas de `seed.py`, pero eso no está confirmado por API.

### Por qué el Quality Gate pasó a ERROR

Es la única condición que falla: `new_coverage` = 0.0% con umbral mínimo 80%. En el primer análisis no había
"código nuevo" de referencia; ahora sí (los cambios de esta tanda) y no hay tests que lo cubran.
Los demás ratings y duplicación sobre código nuevo están OK. No es una regresión de calidad: es consecuencia de no tener tests.
Opciones: escribir tests para las líneas modificadas, o ajustar el Quality Gate (p. ej. quitar la condición
de cobertura sobre código nuevo), o no tratarlo como un fallo en el informe. No toqué la configuración del gate.

### Issues restantes (4)

| Severidad | Archivo | Línea | Regla | Estado |
|---|---|---|---|---|
| MAJOR | chileaid-backend/app/dependencies/auth.py | 75 | python:S1172 | Falso positivo (ver abajo) |
| MAJOR | chileaid-backend/app/services/document_service.py | 41 | python:S1172 | No tocado (ver abajo) |
| INFO | chileaid-backend/app/services/donation_service.py | 192 | python:S1135 | TODO, trabajo pendiente |
| INFO | chileaid-frontend/app/components/org/OrgDashboardView.vue | 192 | Web:S1135 | TODO, trabajo pendiente |

Resueltos: 11 de los 15 issues iniciales.

## Cambios y commits

Por tu indicación "no hagas el commit" dejé de commitear después del tercer punto agrupado. Los puntos 5, 6 y 8 quedan **sin commitear** en el árbol de trabajo.

| # | Punto | Estado | Hash |
|---|---|---|---|
| 1 | Constante para el mensaje de org sin centro (org.py, 4 usos) | commit | `221f751` |
| 2 | Constantes `INSUMO_AGUA_EMBOTELLADA` y `REGION_BIOBIO` (seed.py) | commit | `358c7a0` |
| 3 | `<caption class="sr-only">` en la tabla de AdminCatalogView | commit | `3d36f4e` |
| 4 | `aria-label` en los 6 `<nav>` (Admin, Donor, Org; escritorio y móvil) | commit | `caf36e0` |
| 5 | Eliminado el comentario de HeroSection.vue (L47-49) | sin commit | — |
| 6 | Contraseñas del seed desde `SEED_DEFAULT_PASSWORD` (+ `.env.ejemplo` y `docker-compose.yml`) | sin commit | — |
| 7 | `tipo` en document_service: no se tocó | — | — |
| 8 | Sección del README "Análisis de calidad con SonarQube" | sin commit | — |

Detalles:
- **Punto 4:** en DonorNavbar el elemento marcado es el `<nav>` de la L95 (no la L97, que es el `NuxtLink` interno). Los `aria-label` son "Navegación principal de {administración|donante|organización}" y "Navegación móvil de ...".
- **Punto 5:** el "código comentado" era un comentario explicativo en español sobre el CTA, con comillas y paréntesis que Sonar confundió con código. Se eliminó como pediste.
- **Punto 6:** se quitaron las contraseñas de `ORGANIZACIONES`, `DONANTES` y del admin; todas las cuentas usan `SEED_DEFAULT_PASSWORD`. Si falta o está vacía, `seed()` hace `sys.exit` con un mensaje claro. Se agregó a `.env.ejemplo` (el archivo real se llama `.env.ejemplo`, no `.env.example`) y al servicio `seed` de `docker-compose.yml`; sin esto el seed con Docker habría fallado. No probé el seed contra una base de datos. Las contraseñas anteriores ("admin1234", "org1234", "donante1234") eran distintas por rol; ahora comparten una sola. Si las usas para entrar en la demo, cámbialas por la nueva.

## current_user en auth.py L75 (no tocado)

```python
def get_current_organization_id(
    current_user: User = Depends(require_role(UserRole.ORG)),
    token: str = Depends(oauth2_scheme),
) -> uuid.UUID:
```

El parámetro no se lee en el cuerpo, pero **sí protege los endpoints**. Su valor está en el `Depends(require_role(UserRole.ORG))`: FastAPI lo resuelve antes de ejecutar la función, y `require_role` valida el JWT y responde 403 si el rol no es ORG. Si se quitara el parámetro, `get_current_organization_id` dejaría de verificar el rol y todos los endpoints de `org.py` que dependen de él quedarían sin el chequeo de rol. Es un falso positivo de S1172: la dependencia se usa por su efecto, no por su valor. Se puede reportar así, o dejarlo explícito con `dependencies=[Depends(...)]`/renombrar a `_current_user` si se quisiera silenciar.

## tipo en document_service.py L41 (no tocado)

`get_upload_url(org_id, nombre_archivo, tipo)` **sí recibe el argumento desde un lugar**: `routers/org.py` L288 llama `svc_get_upload_url(organization_id, payload.nombre_archivo, payload.tipo)`, y `tipo` es un campo del schema `DocumentUploadURLRequest` (`"pdf" | "jpg"`). Por tu regla ("si se usa, no lo toques"), lo dejé. Dentro de la función el valor no se usa: la clave del objeto en S3 es `orgs/{org_id}/{uuid}_{nombre_archivo}`, y el tipo real se guarda después en `save_document`. Es un parámetro que se pasa pero se ignora, así que Sonar lo marca con razón. Si quieres quitarlo, habría que cambiar la firma, la llamada del router y decidir si el campo se mantiene en el schema por compatibilidad con el frontend.

## Otras observaciones

- El scanner imprime errores `Cannot read file .../.nuxt/tsconfig.*.json`: el frontend nunca se ha preparado con `nuxt prepare`, así que el análisis TypeScript no tiene los tsconfig generados. El análisis termina con éxito, pero pudo dejar sin analizar reglas que dependen de tipos.
- El README menciona `chileaid-backend/tests/` (189 tests) y `tests/`, pero esas carpetas no existen en este repositorio, por lo que el análisis sigue sin cobertura.
- `sonar-inicial.md`, `sonar-project.properties` y `.scannerwork/` siguen sin versionar.
