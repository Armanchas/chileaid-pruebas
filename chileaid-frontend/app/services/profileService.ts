/**
 * MODEL — Capa de acceso a datos del perfil del donante (AC-01).
 *
 * Conectado al backend real vía `apiFetch` (inyecta `Authorization: Bearer`):
 *   getProfile    → `GET /me/donor`
 *   updateProfile → `PUT /me/donor`
 *
 * El backend resuelve el donante desde el JWT (claim `sub`) y devuelve el
 * `DonorProfileDTO` con estas mismas claves, así que NO hay capa de mapeo de
 * salida. La única adaptación es traducir los errores 4xx (409 email duplicado,
 * 422 validación) a un `UpdateProfileResult` estable. El backend además devuelve
 * `fechaRegistro`, un campo extra que el frontend ignora (no está en la interfaz).
 */

import { apiFetch } from '~/utils/apiFetch'

/** Datos personales del donante autenticado. */
export interface DonorProfileDTO {
  nombre: string
  apellido: string
  email: string
}

/** Payload de edición del perfil enviado desde el formulario. */
export interface UpdateProfileInput {
  nombre: string
  apellido: string
  email: string
}

/** Resultado tipado de un intento de actualización del perfil. */
export interface UpdateProfileResult {
  success: boolean
  profile?: DonorProfileDTO
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

export const profileService = {
  /**
   * Devuelve el perfil del donante autenticado (`GET /me/donor`). El backend
   * resuelve el donante desde el JWT; la respuesta ya trae las claves esperadas
   * → se retorna tal cual (los campos extra como `fechaRegistro` se ignoran).
   */
  async getProfile(): Promise<DonorProfileDTO> {
    return apiFetch<DonorProfileDTO>('/me/donor')
  },

  /**
   * Actualiza los datos personales del donante (`PUT /me/donor`). El backend
   * valida los campos (422) y la unicidad del email (409); cualquier 4xx se
   * traduce a `{ success: false, error }` con el `detail` legible. En éxito
   * devuelve el `DonorProfileDTO` actualizado.
   */
  async updateProfile(input: UpdateProfileInput): Promise<UpdateProfileResult> {
    try {
      const profile = await apiFetch<DonorProfileDTO>('/me/donor', {
        method: 'PUT',
        body: {
          nombre: input.nombre,
          apellido: input.apellido,
          email: input.email
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
