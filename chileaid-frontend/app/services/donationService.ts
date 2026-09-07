/**
 * MODEL — Capa de acceso a datos del flujo de donación por centro.
 *
 * Conectado al backend real vía `apiFetch` (inyecta `Authorization: Bearer`):
 *   createDonation  → `POST /donations`  (CU-05)
 *   getMyDonations  → `GET  /donations`  (CU-06)
 *
 * Es la ÚNICA capa que adapta el contrato: el backend responde con `createdAt`,
 * ítems con `insumoNombre`/`insumoUnidad` y el centro/organización por ítem; aquí
 * se traduce a la forma estable que consumen ViewModels y vistas (`needNombre`,
 * `unidad`, `centerNombre`, `fechaCreacion`). El `codigoSeguimiento` lo genera el
 * BACKEND (RF-01, único y atado a la BD), NUNCA el cliente.
 */
import { apiFetch } from '~/utils/apiFetch'

/**
 * Estado del ciclo de vida de una donación. Coincide EXACTAMENTE con el enum
 * `DonationStatus` del backend: `pendiente` (comprometida, aún sin entregar),
 * `recibido` (confirmada en el centro, CU-07) o `cancelada` (anulada; la donación
 * llega aquí solo cuando todos sus ítems quedan cancelados).
 */
export type DonationEstado = 'pendiente' | 'recibido' | 'cancelada'

/**
 * Quién disparó la cancelación de un ítem, para que el tracking muestre el
 * mensaje correcto. `null` mientras el ítem sigue activo.
 */
export type MotivoCancelacion = 'donante' | 'cierre_necesidad'

/**
 * Un ítem concreto dentro de una donación: la cantidad comprometida de una
 * necesidad puntual del centro, con su nombre y unidad ya resueltos para poder
 * mostrarse sin volver a cruzar entidades. `activo=false` = ítem cancelado
 * (soft), con `motivoCancelacion` indicando quién lo anuló.
 */
export interface DonationItemDTO {
  needId: string
  needNombre: string
  cantidad: number
  unidad: string
  activo: boolean
  motivoCancelacion: MotivoCancelacion | null
}

/**
 * Donación completa: lo que el donante compromete a un centro en una sola
 * entrega. `codigoSeguimiento` (formato `CA-XXXXXXXX`) la identifica de cara al
 * donante; `estado` arranca en `pendiente` al crearse.
 */
export interface DonationDTO {
  id: string
  centerNombre: string
  items: DonationItemDTO[]
  codigoSeguimiento: string
  estado: DonationEstado
  fechaCreacion: string
}

/**
 * Payload de creación de una donación. El ViewModel arma cada ítem con su nombre
 * y unidad resueltos desde el centro cargado (para el resumen en pantalla); al
 * backend solo se le envían `needId` + `cantidad` (lo demás lo resuelve él).
 */
export interface CreateDonationInput {
  centerId: string
  centerNombre: string
  items: {
    needId: string
    needNombre: string
    unidad: string
    cantidad: number
  }[]
}

/** Forma cruda del ítem que devuelve el backend (`DonationItemDTO` de FastAPI). */
interface ApiDonationItem {
  needId: string
  cantidad: number
  insumoNombre: string
  insumoUnidad: string
  centroNombre: string
  organizacionNombre: string
  activo: boolean
  motivoCancelacion: MotivoCancelacion | null
}

/** Forma cruda de la donación que devuelve el backend (`DonationDTO` de FastAPI). */
interface ApiDonation {
  id: string
  codigoSeguimiento: string
  estado: DonationEstado
  items: ApiDonationItem[]
  createdAt: string
  confirmadoAt: string | null
}

/** Envelope de paginación del backend (`Page[DonationDTO]`). */
interface ApiDonationsPage {
  items: ApiDonation[]
  total: number
  limit: number
  offset: number
}

/** Página de donaciones ya adaptada a la forma estable de la UI. */
export interface DonationsPage {
  items: DonationDTO[]
  total: number
}

/**
 * Extrae el mensaje de error del backend. FastAPI responde `{ detail }`: string
 * en los `HTTPException` de negocio (404/409) o array en los 422 de Pydantic.
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

/** Adapta la donación del backend a la forma estable que consume la UI. */
function toDonationDTO(api: ApiDonation): DonationDTO {
  return {
    id: api.id,
    // El aporte va a un único centro; todos sus ítems comparten centro.
    centerNombre: api.items[0]?.centroNombre ?? '',
    items: api.items.map((it) => ({
      needId: it.needId,
      needNombre: it.insumoNombre,
      cantidad: it.cantidad,
      unidad: it.insumoUnidad,
      activo: it.activo,
      motivoCancelacion: it.motivoCancelacion
    })),
    codigoSeguimiento: api.codigoSeguimiento,
    estado: api.estado,
    fechaCreacion: api.createdAt.slice(0, 10) // ISO 8601 → YYYY-MM-DD
  }
}

export const donationService = {
  /**
   * Registra una nueva donación a un centro (`POST /donations`). Solo envía
   * `needId` + `cantidad` por ítem; el backend valida el sobrestock, genera el
   * `codigoSeguimiento` (RF-01) y deja la donación en estado `pendiente`. Un 4xx
   * (necesidad no activa / sobrestock) lo propaga `apiFetch` para que el
   * ViewModel muestre el error.
   */
  async createDonation(input: CreateDonationInput): Promise<DonationDTO> {
    const api = await apiFetch<ApiDonation>('/donations', {
      method: 'POST',
      body: {
        items: input.items.map((i) => ({ needId: i.needId, cantidad: i.cantidad }))
      }
    })
    return toDonationDTO(api)
  },

  /**
   * Página de donaciones del donante autenticado, más recientes primero
   * (`GET /donations?limit=&offset=`). El backend filtra por el donante del JWT.
   */
  async getMyDonations(params: { limit: number; offset: number }): Promise<DonationsPage> {
    const api = await apiFetch<ApiDonationsPage>('/donations', {
      query: { limit: params.limit, offset: params.offset }
    })
    return { items: api.items.map(toDonationDTO), total: api.total }
  },

  /**
   * Cancela (soft) una donación pendiente del donante (`POST /donations/{id}/cancel`).
   * Devuelve la donación ya en estado `cancelada`. Un 404 (no existe / no le
   * pertenece) o 409 (ya recibida / ya cancelada) lo propaga `apiFetch` para que
   * el ViewModel muestre el error.
   */
  async cancelDonation(id: string): Promise<DonationDTO> {
    try {
      const api = await apiFetch<ApiDonation>(`/donations/${id}/cancel`, {
        method: 'POST'
      })
      return toDonationDTO(api)
    } catch (err) {
      throw new Error(apiErrorMessage(err, 'No se pudo cancelar la donación.'))
    }
  }
}
