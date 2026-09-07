/**
 * MODEL — Capa de acceso a datos del perfil de la organización receptora (CU-09).
 *
 * Conectado al backend real vía `apiFetch` (inyecta `Authorization: Bearer`):
 *   getOrgProfile    → `GET /org/profile`
 *   updateOrgProfile → `PUT /org/profile`
 *
 * El backend resuelve la org desde el JWT (claim `organization_id`) y devuelve el
 * `OrgProfileDTO` con esta misma forma (claves camelCase), así que NO hay capa de
 * mapeo de salida. La única adaptación es traducir los errores 4xx (409 email
 * duplicado, 422 validación) a un `UpdateOrgProfileResult` estable.
 *
 * Los datos de identidad (`nombre`, `tipo`, `rut`, `documentacion`) se fijan en el
 * registro (CU-01) y NO son editables desde el perfil: solo los datos de contacto
 * (`contactoNombre`, `email`, `telefono`, `region`) se pueden actualizar.
 */

import { apiFetch } from '~/utils/apiFetch'

/** Función que cumple la organización dentro de la red de ayuda. */
export type OrgType = 'centro_acopio' | 'punto_distribucion' | 'ambos'

/** Estado de verificación de la organización dentro de la plataforma. */
export type OrgEstado = 'pendiente' | 'activa' | 'rechazada' | 'inactiva'

/** Perfil completo de la organización receptora autenticada. */
export interface OrgProfileDTO {
  id: string
  nombre: string
  tipo: OrgType
  rut: string
  contactoNombre: string
  email: string
  telefono: string
  documentacion: string // nombre del archivo subido
  estado: OrgEstado
  fechaRegistro: string // ISO YYYY-MM-DD
  region: string
  // Motivo cuando el admin rechaza la org (CU-02); null si no fue rechazada.
  motivoRechazo: string | null
}

/**
 * Payload de edición del perfil. Solo incluye los datos de contacto editables;
 * `nombre`, `tipo`, `rut` y `documentacion` quedan fijados en el registro.
 */
export interface UpdateOrgProfileInput {
  contactoNombre: string
  email: string
  telefono: string
  region: string
}

/** Resultado tipado de un intento de actualización del perfil. */
export interface UpdateOrgProfileResult {
  success: boolean
  profile?: OrgProfileDTO
  error?: string
}

/**
 * Extrae un mensaje legible del error que lanza `apiFetch`/`$fetch`. FastAPI
 * responde `{ detail }`: un string en nuestros `HTTPException` de negocio (409
 * email duplicado) o un array en los 422 de validación de Pydantic. Cae al
 * `fallback` si no hay forma reconocible.
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

export const orgProfileService = {
  /**
   * Devuelve el perfil de la organización autenticada (`GET /org/profile`). El
   * backend resuelve la org desde el JWT; la respuesta ya es el `OrgProfileDTO`
   * unificado → se retorna tal cual.
   */
  async getOrgProfile(): Promise<OrgProfileDTO> {
    return apiFetch<OrgProfileDTO>('/org/profile')
  },

  /**
   * Actualiza los datos de contacto de la organización (`PUT /org/profile`). El
   * backend valida los campos (422) y la unicidad del email (409); cualquier 4xx
   * se traduce a `{ success: false, error }` con el `detail` legible. En éxito
   * devuelve el `OrgProfileDTO` actualizado.
   */
  async updateOrgProfile(
    input: UpdateOrgProfileInput
  ): Promise<UpdateOrgProfileResult> {
    try {
      const profile = await apiFetch<OrgProfileDTO>('/org/profile', {
        method: 'PUT',
        body: {
          contactoNombre: input.contactoNombre,
          email: input.email,
          telefono: input.telefono,
          region: input.region
        }
      })
      return { success: true, profile }
    } catch (err) {
      return {
        success: false,
        error: apiErrorMessage(err, 'No se pudieron guardar los cambios.')
      }
    }
  }
}
