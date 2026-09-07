/**
 * MODEL — Capa de acceso a datos del panel de la organización receptora.
 *
 * `getOrgCenter` ya consume el backend real (`GET /org/center`) vía `apiFetch`: el
 * contrato del backend es la FUENTE DE VERDAD y se adopta 1:1, sin mapeo. Un 404
 * ("la organización aún no tiene un centro") se traduce a `null`, no a error.
 *
 * Las recepciones (CU-07) migraron a `orgReceptionsService` (conectado a
 * `/org/receptions/*`); ya no viven aquí.
 *
 * Aquí viven los tipos de dominio COMPARTIDOS del centro y sus necesidades
 * (`OrgCenterDTO`, `NeedDTO`, `InsumoDTO`, `Urgencia`…), reutilizados por
 * `orgNeedsService`. El `NeedDTO` es único en todo el frontend; no se redefine.
 *
 * Concepto clave del dominio: la `cobertura` (0-100) indica qué porcentaje de la
 * meta de donaciones está cubierto. NUNCA se llama "saturación".
 */

import { apiFetch } from '~/utils/apiFetch'

/** Nivel de urgencia de una necesidad (enum del backend). */
export type Urgencia = 'alta' | 'media' | 'baja'

/** Estado de saturación del centro, derivado de la cobertura agregada. */
export type OrgCenterEstado = 'critico' | 'en_capacidad' | 'cerrado'

/**
 * Función que cumple la organización dentro de la red de ayuda. NO forma parte de
 * `OrgCenterDTO` (el backend no lo expone en `/org/center`); se conserva porque
 * `distributionService` lo reutiliza para su propia unión `OrgType`.
 */
export type OrgTipoCentro = 'centro_acopio' | 'punto_distribucion' | 'ambos'

/** Insumo del catálogo referenciado por una necesidad (datos denormalizados). */
export interface InsumoDTO {
  nombre: string
  categoria: string
  unidad: string
}

/**
 * Necesidad de un centro — forma ÚNICA en todo el frontend, espejo del `NeedDTO`
 * del backend. `cobertura` (0-100) la deriva el backend de
 * `cantidadComprometida / cantidadRequerida`.
 */
export interface NeedDTO {
  id: string
  insumo: InsumoDTO
  cantidadRequerida: number
  cantidadComprometida: number
  cantidadRecibida: number
  urgencia: Urgencia
  estado: string
  cobertura: number
}

/** Agregados del centro: suma de sus necesidades + cobertura general derivada. */
export interface CenterTotalesDTO {
  cantidadRequerida: number
  cantidadComprometida: number
  cantidadRecibida: number
  coberturaGeneral: number
}

/**
 * Emergencia a la que responde el centro (referencia mínima para el badge).
 * `estado` distingue un vínculo vigente (`activa`) de uno histórico (`cerrada`).
 */
export interface OrgCenterEmergencia {
  id: string
  nombre: string
  estado: 'activa' | 'cerrada'
}

/** Centro de acopio de la organización autenticada (espejo de `GET /org/center`). */
export interface OrgCenterDTO {
  id: string
  nombre: string
  direccion: string
  zona: string
  horarioAtencion: string | null
  estado: OrgCenterEstado
  latitud: number | null
  longitud: number | null
  emergencia: OrgCenterEmergencia | null
  necesidades: NeedDTO[]
  totales: CenterTotalesDTO
}

/**
 * Datos que el formulario envía para crear/editar el centro de la org
 * (`POST/PUT /org/center`). `horarioAtencion` y las coordenadas son opcionales;
 * el backend exige las coordenadas juntas (ambas o ninguna) y dentro de rango.
 * `emergencyId` (nullable) vincula el centro a una emergencia ACTIVA; `null`
 * desvincula. La lista de emergencias activas se obtiene de `GET /emergencies`.
 */
export interface CreateCenterInput {
  nombre: string
  direccion: string
  zona: string
  horarioAtencion?: string | null
  latitud?: number | null
  longitud?: number | null
  emergencyId?: string | null
}

/**
 * Extrae un mensaje legible del error que lanza `apiFetch`/`$fetch`. FastAPI
 * responde `{ detail }`: un string en los `HTTPException` de negocio (409 centro
 * duplicado) o un array en los 422 de validación de Pydantic. Cae al `fallback`
 * si no hay forma reconocible.
 */
function apiErrorMessage(err: unknown, fallback: string): string {
  const detail = (err as { data?: { detail?: unknown } })?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0] as { msg?: string }
    if (typeof first?.msg === 'string') return first.msg
  }
  return fallback
}

/** Opción del selector de emergencia del formulario del centro. */
export interface ActiveEmergencyOption {
  id: string
  nombre: string
}

/** Punto sugerido por el geocoder para una dirección (`GET /geocode`, RF-05). */
export interface GeocodeResult {
  latitud: number
  longitud: number
  displayName: string
}

export const orgDashboardService = {
  /**
   * Emergencias ACTIVAS para el selector del formulario del centro
   * (`GET /emergencies?estado=activa`, endpoint público). La org solo puede
   * vincular su centro a una emergencia activa; devuelve solo `{ id, nombre }`.
   */
  async getActiveEmergencies(): Promise<ActiveEmergencyOption[]> {
    const list = await apiFetch<{ id: string; nombre: string }[]>('/emergencies', {
      query: { estado: 'activa' }
    })
    return list.map((e) => ({ id: e.id, nombre: e.nombre }))
  },

  /**
   * Geocodifica una dirección a un punto sugerido (`GET /geocode`, RF-05) para
   * el selector de mapa del formulario del centro. Devuelve `null` si el backend
   * no encontró la dirección o el geocoder falló (la org puede ubicar el punto a
   * mano en el mapa). Requiere sesión de org (el endpoint está gateado).
   */
  async geocodeAddress(query: string): Promise<GeocodeResult | null> {
    const q = query.trim()
    if (q.length < 3) return null
    try {
      return await apiFetch<GeocodeResult | null>('/geocode', { query: { q } })
    } catch {
      // Comodidad, no bloqueante: ante cualquier error, el picker sigue a mano.
      return null
    }
  },

  /**
   * Devuelve el centro de la organización autenticada (`GET /org/center`). El
   * `organization_id` lo resuelve el backend desde el JWT. Devuelve `null` si la
   * org aún no tiene centro (404), para que la vista muestre el estado "sin
   * centro" en vez de un error.
   */
  async getOrgCenter(): Promise<OrgCenterDTO | null> {
    try {
      return await apiFetch<OrgCenterDTO>('/org/center')
    } catch (err) {
      const status =
        (err as { statusCode?: number })?.statusCode ??
        (err as { response?: { status?: number } })?.response?.status
      if (status === 404) return null
      throw err
    }
  },

  /**
   * Crea el centro de la organización autenticada (`POST /org/center`, 201). Solo
   * tiene sentido cuando la org aún no tiene centro (estado "sin centro"). Devuelve
   * el `OrgCenterDTO` recién creado (mismo shape que `getOrgCenter`). Un 4xx (409
   * si ya existe, 422 de validación) se traduce a un `Error` con el `detail` del
   * backend para que el VM lo muestre en el formulario.
   */
  async createCenter(input: CreateCenterInput): Promise<OrgCenterDTO> {
    try {
      return await apiFetch<OrgCenterDTO>('/org/center', {
        method: 'POST',
        body: {
          nombre: input.nombre,
          direccion: input.direccion,
          zona: input.zona,
          horarioAtencion: input.horarioAtencion ?? null,
          latitud: input.latitud ?? null,
          longitud: input.longitud ?? null,
          emergencyId: input.emergencyId ?? null
        }
      })
    } catch (err) {
      throw new Error(apiErrorMessage(err, 'No se pudo crear el centro.'))
    }
  },

  /**
   * Edita el centro de la organización autenticada (`PUT /org/center`). Mismo
   * shape de entrada que `createCenter` (los campos editables) y misma forma de
   * salida (`OrgCenterDTO`). 404 si la org aún no tiene centro (debería usar
   * `createCenter`); 422 de validación → `Error(detail)` para el formulario.
   */
  async updateCenter(input: CreateCenterInput): Promise<OrgCenterDTO> {
    try {
      return await apiFetch<OrgCenterDTO>('/org/center', {
        method: 'PUT',
        body: {
          nombre: input.nombre,
          direccion: input.direccion,
          zona: input.zona,
          horarioAtencion: input.horarioAtencion ?? null,
          latitud: input.latitud ?? null,
          longitud: input.longitud ?? null,
          emergencyId: input.emergencyId ?? null
        }
      })
    } catch (err) {
      throw new Error(apiErrorMessage(err, 'No se pudo actualizar el centro.'))
    }
  }
}
