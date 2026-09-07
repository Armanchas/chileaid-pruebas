/**
 * MODEL — Capa de acceso a datos de autenticación.
 *
 * `login` y `registerOrganization` ya consumen el backend real (`POST
 * /auth/login`, `POST /auth/register/org`) vía `apiFetch`; son la ÚNICA capa que
 * adapta el contrato (traducir `{ access_token }` + el claim `role` del JWT a
 * `AuthResult`; traducir los 4xx del registro a un `RegisterResult` con mensaje
 * legible). `registerDonor` sigue mockeado con `simulateNetwork` hasta que exista
 * su endpoint.
 */

import { apiFetch } from '~/utils/apiFetch'
import { decodeJwtPayload } from '~/utils/jwt'

/** Credenciales que el usuario envía desde el formulario. */
export interface AuthCredentials {
  email: string
  password: string
}

/** Rol con el que se resuelve la sesión, según el tipo de cuenta. */
export type AuthRole = 'donor' | 'org' | 'admin'

/** Resultado tipado de un intento de autenticación. */
export interface AuthResult {
  success: boolean
  token?: string
  role?: AuthRole
  error?: string
}

/** Respuesta cruda del backend en `POST /auth/login` (antes de adaptar a `AuthResult`). */
interface LoginResponse {
  access_token: string
  token_type: string
}

/** Respuesta de `GET /auth/me` (§1.7): identidad verificada server-side. */
export interface MeResult {
  id: string
  role: AuthRole
  organizationId: string | null
}

/** Datos que el donante envía desde el formulario de registro. */
export interface DonorRegisterData {
  nombre: string
  apellido: string
  email: string
  password: string
  confirmPassword: string
}

/** Función que cumple la organización dentro de la red de ayuda. */
export type TipoCentro = 'centro_acopio' | 'punto_distribucion' | 'ambos'

/**
 * Datos que una organización envía desde el formulario de registro (CU-01).
 *
 * Espejo del `OrgRegisterRequest` del backend (`POST /auth/register/org`): 9
 * campos en tres secciones (organización · contacto · credenciales), `rut`
 * opcional. La org queda en estado "Pendiente" hasta que el equipo de Chile Aid
 * la verifique. El documento de respaldo NO viaja en este payload — se sube
 * aparte (flujo de presigned URL) usando el token que devuelve el registro; ver
 * `useOrgRegisterViewModel.submit`.
 */
export interface OrgRegisterPayload {
  // Datos de la organización
  nombre: string
  tipoCentro: TipoCentro
  rut?: string
  region: string
  direccion: string
  // Datos de contacto
  contactoNombre: string
  email: string
  telefono: string
  // Credenciales
  password: string
  confirmPassword: string
}

/**
 * Extrae un mensaje legible del error que lanza `apiFetch`/`$fetch`. FastAPI
 * responde `{ detail }`: un string en los `HTTPException` de negocio o un array
 * en los 422 de validación de Pydantic. Cae al `fallback` si no es reconocible.
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

/**
 * Resultado tipado de un intento de registro.
 *
 * `token` viene poblado tanto para donante como para organización: en el caso
 * de la org, el JWT autoriza la subida del documento de respaldo en el mismo
 * flujo de registro, aunque la cuenta siga "Pendiente" hasta la aprobación del
 * admin (el token no la activa, solo habilita `/org/documents/*` de entrada).
 */
export interface RegisterResult {
  success: boolean
  token?: string | null
  error?: string
}

export const authService = {
  /**
   * Autentica a un usuario contra `POST /auth/login`.
   *
   * El backend responde `{ access_token, token_type }`; el `role` NO viene en el
   * body, viaja como claim del JWT (`sub`, `role`, y `organization_id` solo para
   * orgs). Por eso decodificamos el payload del token (sin validar firma) para
   * extraer el rol. En error, `$fetch` lanza: el 401 trae `{ detail }` que
   * mostramos al usuario.
   */
  async login(credentials: AuthCredentials): Promise<AuthResult> {
    try {
      const data = await apiFetch<LoginResponse>('/auth/login', {
        method: 'POST',
        body: {
          email: credentials.email.trim(),
          password: credentials.password
        }
      })

      const payload = decodeJwtPayload(data.access_token)
      const claimRole = payload?.role
      let role: AuthRole
      if (claimRole === 'donor' || claimRole === 'org' || claimRole === 'admin') {
        role = claimRole
      } else {
        console.warn('[ChileAid] El JWT no trae un "role" válido; se asume "donor".')
        role = 'donor'
      }

      return { success: true, token: data.access_token, role }
    } catch (err) {
      const detail = (err as { data?: { detail?: string } })?.data?.detail
      return {
        success: false,
        error: detail ?? 'No se pudo iniciar sesión. Verifica tu correo y contraseña.'
      }
    }
  },

  /**
   * Valida el token contra `GET /auth/me` (§1.7) y devuelve la identidad que el
   * backend verificó server-side (firma + expiración), a diferencia del decode
   * optimista de `login` (§2.2: ese decode client-side no valida firma). `null`
   * si el token no es válido o la request falla — `apiFetch` ya cierra la
   * sesión automáticamente ante un 401 con token presente.
   */
  async getMe(): Promise<MeResult | null> {
    try {
      return await apiFetch<MeResult>('/auth/me')
    } catch {
      return null
    }
  },

  /**
   * Registra un nuevo donante contra `POST /auth/register/donor`.
   *
   * A diferencia del registro de org, el donante recibe un JWT de inmediato
   * (sin esperar aprobación). El backend valida email único (409) y que
   * password == confirmPassword (422).
   */
  async registerDonor(data: DonorRegisterData): Promise<RegisterResult> {
    try {
      const response = await apiFetch<{ access_token: string }>('/auth/register/donor', {
        method: 'POST',
        body: {
          nombre: data.nombre,
          apellido: data.apellido,
          email: data.email,
          password: data.password,
          confirmPassword: data.confirmPassword
        }
      })
      return { success: true, token: response.access_token }
    } catch (err) {
      const status =
        (err as { statusCode?: number })?.statusCode ??
        (err as { response?: { status?: number } })?.response?.status

      if (status === 409) {
        return { success: false, error: 'Ya existe una cuenta con ese correo.' }
      }
      return {
        success: false,
        error: apiErrorMessage(err, 'No se pudo completar el registro.')
      }
    }
  },

  /**
   * Registra una organización receptora (`POST /auth/register/org`, CU-01).
   *
   * La org nace en estado "Pendiente" hasta que un admin la apruebe, pero el
   * backend sí devuelve un JWT (igual al de login) para que el flujo de
   * registro pueda subir el documento de respaldo de inmediato — ver
   * `useOrgRegisterViewModel.submit`. El backend valida los campos (422) y la
   * unicidad del email (409); cualquier 4xx se traduce a
   * `{ success: false, error }` con un mensaje legible para el formulario.
   */
  async registerOrganization(payload: OrgRegisterPayload): Promise<RegisterResult> {
    try {
      const response = await apiFetch<{ success: boolean; token: string | null }>(
        '/auth/register/org',
        {
          method: 'POST',
          body: {
            nombre: payload.nombre,
            tipoCentro: payload.tipoCentro,
            rut: payload.rut,
            region: payload.region,
            direccion: payload.direccion,
            contactoNombre: payload.contactoNombre,
            email: payload.email,
            telefono: payload.telefono,
            password: payload.password,
            confirmPassword: payload.confirmPassword
          }
        }
      )
      return { success: true, token: response.token }
    } catch (err) {
      const status =
        (err as { statusCode?: number })?.statusCode ??
        (err as { response?: { status?: number } })?.response?.status

      // El 409 (email ya registrado) se muestra con un mensaje propio del flujo;
      // el resto (422 de validación, etc.) reusa el `detail` del backend.
      if (status === 409) {
        return { success: false, error: 'Ya existe una cuenta con ese email.' }
      }
      return {
        success: false,
        error: apiErrorMessage(err, 'No se pudo enviar la solicitud.')
      }
    }
  }
}
