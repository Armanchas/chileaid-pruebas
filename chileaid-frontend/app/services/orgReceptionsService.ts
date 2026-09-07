/**
 * MODEL — Acceso a datos de las recepciones de la organización (CU-07).
 *
 * Conectado al backend real vía `apiFetch` (inyecta `Authorization: Bearer`; la
 * org se resuelve del JWT):
 *   getPendingReceptions → `GET  /org/receptions/pending`
 *   confirmReception     → `POST /org/receptions/confirm`  body `{ codigo }`
 *
 * El backend aísla por organización (cada org solo ve/confirma donaciones de su
 * propio centro). `confirmReception` traduce los errores de negocio del backend
 * (404 código inexistente, 403 de otro centro, 409 ya recibido) a un
 * `ConfirmReceptionResult` `{ success:false, error }` para que el ViewModel los
 * muestre sin romper.
 */
import { apiFetch } from '~/utils/apiFetch'

/** Línea de una recepción pendiente: insumo y cantidad comprometida. */
export interface ReceptionItemDTO {
  needId: string
  insumoNombre: string
  cantidad: number
}

/**
 * Recepción pendiente: una donación comprometida (estado `pendiente`) del centro
 * de la org, lista para confirmar. `codigoSeguimiento` (formato `CA-XXXXXXXX`) la
 * identifica al confirmar; `createdAt` es la fecha del compromiso (ISO).
 */
export interface PendingReceptionDTO {
  donationId: string
  codigoSeguimiento: string
  items: ReceptionItemDTO[]
  createdAt: string
}

/** Resultado tipado de un intento de confirmar una recepción. */
export interface ConfirmReceptionResult {
  success: boolean
  error?: string
}

/**
 * Extrae un mensaje legible del error que lanza `apiFetch`/`$fetch`. FastAPI
 * responde `{ detail }`: un string en los `HTTPException` de negocio (404/403/409)
 * o un array en los 422 de validación de Pydantic.
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

export const orgReceptionsService = {
  /**
   * Donaciones pendientes de confirmar del centro de la org autenticada
   * (`GET /org/receptions/pending`). Lista vacía si la org no tiene centro o no
   * tiene pendientes.
   */
  async getPendingReceptions(): Promise<PendingReceptionDTO[]> {
    return apiFetch<PendingReceptionDTO[]>('/org/receptions/pending')
  },

  /**
   * Confirma la recepción de una donación por su código
   * (`POST /org/receptions/confirm`). En éxito el backend marca la donación como
   * `recibido` e incrementa la cantidad recibida de cada necesidad. Un 4xx
   * (404/403/409) se traduce a `{ success:false, error }` con el `detail`.
   */
  async confirmReception(codigo: string): Promise<ConfirmReceptionResult> {
    const code = codigo.trim()
    if (!code) {
      return { success: false, error: 'Ingresa un código' }
    }
    try {
      await apiFetch('/org/receptions/confirm', {
        method: 'POST',
        body: { codigo: code }
      })
      return { success: true }
    } catch (err) {
      return {
        success: false,
        error: apiErrorMessage(err, 'No se pudo confirmar la recepción.')
      }
    }
  }
}
