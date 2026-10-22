# Análisis inicial SonarQube — ChileAid

- Servidor: SonarQube 9.9 Community (http://localhost:9100), proyecto `chileaid`, rama `main`
- Fecha del análisis: 2026-10-22 (UTC)
- Alcance: 181 archivos (backend `chileaid-backend/app` + `seed.py`, frontend `chileaid-frontend/app`)
- Ver resultados: http://localhost:9100/dashboard?id=chileaid

## Resumen

| Métrica | Valor | Fuente |
|---|---|---|
| Quality Gate | **OK (Passed)** | API `qualitygates/project_status` |
| Bugs | **1** (MINOR) | API `issues/search` |
| Vulnerabilities | **0** | API `issues/search` |
| Code Smells | **14** | API `issues/search` |
| Deuda técnica estimada | 72 min | API `issues/search` (effortTotal) |
| Coverage | No disponible por API (ver nota); el repo no tiene tests, así que no hay reporte de cobertura | — |
| Duplications % | No disponible por API (ver nota) | — |
| Maintainability / Security / Reliability Rating | No disponibles por API (ver nota) | — |
| Security Hotspots | No disponible por API (ver nota) | — |

> **Nota — datos faltantes:** el token entregado (`sqp_...`) es de tipo *Project Analysis Token*.
> Sirve para subir análisis y leer issues y Quality Gate, pero `/api/measures/component`,
> `measures/component_tree`, `measures/search_history` y `hotspots/search` responden
> `Insufficient privileges`. No intenté otras credenciales. Esos valores se leen directamente
> en http://localhost:9100/dashboard?id=chileaid, o se pueden obtener con un token de usuario
> (My Account → Security → User Token).

## Tests y cobertura

No hay tests en el repositorio (ni pytest en backend ni Vitest/Jest en frontend; solo existen `pytest` y `httpx`
en `requirements-dev.txt`, sin archivos de test). Por eso no se generó `coverage.xml` ni `lcov`, y
`sonar-project.properties` no define `reportPaths` de cobertura.

## Configuración usada

`sonar-project.properties` en la raíz:
- `sonar.sources=chileaid-backend/app,chileaid-backend/seed.py,chileaid-frontend/app`
- Exclusiones: `node_modules`, `.nuxt`, `.output`, `__pycache__`, `venv/.venv`, `alembic/versions` (migraciones), `dist`, `coverage`, `*.min.js`, `*.d.ts`, `public`, `assets`

## Issues (15 en total, ordenados por severidad)

Distribución: BLOCKER 0 · CRITICAL 3 · MAJOR 9 · MINOR 1 · INFO 2

### CRITICAL (3)

| Archivo | Línea | Regla | Descripción |
|---|---|---|---|
| chileaid-backend/seed.py | 58 | python:S1192 | Definir una constante en lugar de duplicar el literal "Agua embotellada" (3 veces) |
| chileaid-backend/seed.py | 81 | python:S1192 | Definir una constante en lugar de duplicar el literal "Bío Bío" (4 veces) |
| chileaid-backend/app/routers/org.py | 88 | python:S1192 | Definir una constante en lugar de duplicar el literal "La organización aún no tiene un centro registrado" (4 veces) |

### MAJOR (9)

| Archivo | Línea | Regla | Descripción |
|---|---|---|---|
| chileaid-backend/app/dependencies/auth.py | 75 | python:S1172 | Eliminar el parámetro no usado `current_user` |
| chileaid-backend/app/services/document_service.py | 41 | python:S1172 | Eliminar el parámetro no usado `tipo` |
| chileaid-frontend/app/components/donor/DonorNavbar.vue | 39 | Web:S5255 | Falta `aria-label`/`aria-labelledby` en el elemento |
| chileaid-frontend/app/components/donor/DonorNavbar.vue | 95 | Web:S5255 | Ídem |
| chileaid-frontend/app/components/org/OrgNavbar.vue | 39 | Web:S5255 | Ídem |
| chileaid-frontend/app/components/org/OrgNavbar.vue | 105 | Web:S5255 | Ídem |
| chileaid-frontend/app/components/admin/AdminNavbar.vue | 38 | Web:S5255 | Ídem |
| chileaid-frontend/app/components/admin/AdminNavbar.vue | 103 | Web:S5255 | Ídem |
| chileaid-frontend/app/components/landing/HeroSection.vue | 47 | Web:AvoidCommentedOutCodeCheck | Eliminar código comentado |

### MINOR (1) — Bug

| Archivo | Línea | Regla | Descripción |
|---|---|---|---|
| chileaid-frontend/app/components/admin/AdminCatalogView.vue | 203 | Web:TableWithoutCaptionCheck | Agregar una descripción (caption) a la tabla |

### INFO (2)

| Archivo | Línea | Regla | Descripción |
|---|---|---|---|
| chileaid-backend/app/services/donation_service.py | 192 | python:S1135 | Completar la tarea del comentario TODO |
| chileaid-frontend/app/components/org/OrgDashboardView.vue | 192 | Web:S1135 | Completar la tarea del comentario TODO |

## Notas

- No se corrigió ningún archivo del proyecto. Lo único creado: `sonar-project.properties` y este informe.
- El scanner en Docker también creó la carpeta `.scannerwork/` en la raíz (no está en `.gitignore`).
