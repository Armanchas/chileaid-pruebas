import type { FetchOptions } from 'ofetch'

/**
 * Wrapper de `$fetch` para hablar con la API real (FastAPI).
 *
 * Centraliza tres cosas transversales para que los services no las repitan:
 *  - `baseURL` desde `runtimeConfig.public.apiBase`.
 *  - Header `Authorization: Bearer <token>` si hay sesión activa (o el `authToken`
 *    explícito, para llamadas autenticadas fuera de una sesión persistida —p. ej.
 *    subir el documento de respaldo justo después del registro de organización,
 *    con el JWT recién emitido y sin pasar por `useAuth().login`).
 *  - Cierre de sesión automático ante un 401 con sesión presente (token vencido /
 *    inválido): limpia la sesión y redirige a /login.
 *
 * Los demás errores (403, 404, 500, o un 401 SIN sesión —típico de un login con
 * credenciales malas—) se propagan tal cual: cada service decide cómo tratarlos.
 */
export async function apiFetch<T>(
  request: string,
  options: FetchOptions = {},
  authToken?: string
): Promise<T> {
  const config = useRuntimeConfig()
  const { token, logout } = useAuth()

  // En SSR el backend puede no estar en "localhost" (p. ej. Docker): se usa la
  // base privada del servidor; en el navegador, la pública.
  const baseURL = import.meta.server ? config.apiBaseServer : config.public.apiBase

  const bearer = authToken ?? token.value
  const headers = new Headers(options.headers as HeadersInit)
  if (bearer) {
    headers.set('Authorization', `Bearer ${bearer}`)
  }

  try {
    return await $fetch<T>(request, {
      baseURL,
      ...options,
      headers
    })
  } catch (err) {
    const status =
      (err as { statusCode?: number })?.statusCode ??
      (err as { response?: { status?: number } })?.response?.status

    // 401 con sesión activa = el token dejó de ser válido → cerrar sesión. Un 401
    // sin token de sesión (ej. login fallido, o un authToken explícito que no
    // pasa por useAuth) NO dispara logout: se propaga al service.
    if (status === 401 && token.value) {
      await logout()
    }
    throw err
  }
}
