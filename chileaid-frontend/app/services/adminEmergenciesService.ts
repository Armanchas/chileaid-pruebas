/**
 * MODEL — Capa de acceso a datos de la gestión de EMERGENCIAS por el
 * administrador.
 *
 * Conectado al backend real vía `apiFetch` (inyecta `Authorization: Bearer`):
 *   getEmergencies  → `GET  /admin/emergencies`         (activas Y cerradas)
 *   createEmergency → `POST /admin/emergencies`         (nace activa)
 *   closeEmergency  → `POST /admin/emergencies/{id}/close`
 *
 * El admin es dueño solo del CATÁLOGO de emergencias (crear/listar/cerrar); el
 * vínculo centro↔emergencia lo hace cada organización desde su propio centro
 * (`orgDashboardService`), no el admin. El `EmergencyDTO` se reutiliza del
 * dominio del donante (mismo contrato del backend, con agregados derivados).
 */
import { apiFetch } from '~/utils/apiFetch'
import {
  type EmergencyDTO,
  type EmergencyStatus,
  type EmergencyType
} from '~/services/donorCentersService'

// Reutiliza el contrato de emergencia: mismo DTO en todo el dominio.
export type { EmergencyDTO, EmergencyStatus, EmergencyType }

/** Datos que el formulario envía para dar de alta una emergencia. */
export interface CreateEmergencyInput {
  nombre: string
  /** value del enum EmergencyType del backend. */
  tipo: EmergencyType
  zona: string
  /** Fecha ISO 'YYYY-MM-DD'. */
  fechaInicio: string
}

/**
 * Tipos de emergencia: `value` calza EXACTAMENTE con el enum `EmergencyType` del
 * backend; `label` es el texto que ve el admin. El `<select>` del modal envía el
 * `value`.
 */
export const TIPOS_EMERGENCIA: { value: EmergencyType; label: string }[] = [
  { value: 'terremoto', label: 'Terremoto' },
  { value: 'incendio', label: 'Incendio' },
  { value: 'aluvion', label: 'Aluvión' },
  { value: 'otro', label: 'Otro' }
]

/**
 * Extrae un mensaje legible del error que lanza `apiFetch`/`$fetch`. FastAPI
 * responde `{ detail }`: string en los `HTTPException` de negocio (404/409) o un
 * array en los 422 de validación de Pydantic.
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

export const adminEmergenciesService = {
  /**
   * Emergencias para gestión (`GET /admin/emergencies`): activas y cerradas
   * (historial). `estado` opcional filtra (`activa`/`cerrada`).
   */
  async getEmergencies(estado?: EmergencyStatus): Promise<EmergencyDTO[]> {
    return apiFetch<EmergencyDTO[]>('/admin/emergencies', {
      query: estado ? { estado } : undefined
    })
  },

  /**
   * Crea una emergencia (`POST /admin/emergencies`). Relanza un `Error` con el
   * mensaje del backend en un 422 de validación, para mostrarlo en el modal.
   */
  async createEmergency(input: CreateEmergencyInput): Promise<EmergencyDTO> {
    try {
      return await apiFetch<EmergencyDTO>('/admin/emergencies', {
        method: 'POST',
        body: {
          nombre: input.nombre,
          tipo: input.tipo,
          zona: input.zona,
          fechaInicio: input.fechaInicio
        }
      })
    } catch (err) {
      throw new Error(apiErrorMessage(err, 'No se pudo crear la emergencia.'))
    }
  },

  /**
   * Cierra una emergencia (`POST /admin/emergencies/{id}/close`). Devuelve el DTO
   * ya `cerrada`. NO lanza: un 404/409 se traduce a `{ success:false, error }`
   * para que el ViewModel lo muestre sin recargar.
   */
  async closeEmergency(
    id: string
  ): Promise<{ success: boolean; emergency?: EmergencyDTO; error?: string }> {
    try {
      const emergency = await apiFetch<EmergencyDTO>(
        `/admin/emergencies/${id}/close`,
        { method: 'POST' }
      )
      return { success: true, emergency }
    } catch (err) {
      return {
        success: false,
        error: apiErrorMessage(err, 'No se pudo cerrar la emergencia.')
      }
    }
  }
}
