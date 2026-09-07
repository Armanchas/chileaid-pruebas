import { computed } from 'vue'
import type { AuthRole } from '~/services/authService'

/**
 * Composable de sesión — única fuente de verdad de la autenticación.
 *
 * Combina `useState` (estado reactivo compartido durante la vida de la app) con
 * `useCookie` (persistencia entre recargas). La cookie NO es httpOnly —no es
 * posible desde el cliente—; usa `sameSite: 'lax'` y `secure` solo fuera de dev
 * (las cookies `secure` no viajan por http://localhost).
 *
 * El token se guarda tal cual lo emite el backend; el `role` se extrae del claim
 * del JWT en `authService.login` y se persiste aquí para enrutar/proteger sin
 * volver a decodificar.
 */

const COOKIE_MAX_AGE = 60 * 60 * 24 * 7 // 7 días

export function useAuth() {
  const cookieOpts = {
    maxAge: COOKIE_MAX_AGE,
    sameSite: 'lax' as const,
    secure: !import.meta.dev
  }

  const tokenCookie = useCookie<string | null>('chileaid_token', cookieOpts)
  const roleCookie = useCookie<AuthRole | null>('chileaid_role', cookieOpts)

  // `useState` se siembra desde la cookie: en SSR y tras una recarga la sesión
  // persistida queda disponible sin trabajo extra del llamador.
  const token = useState<string | null>('auth.token', () => tokenCookie.value ?? null)
  const role = useState<AuthRole | null>('auth.role', () => roleCookie.value ?? null)

  const isAuthenticated = computed<boolean>(() => token.value !== null)

  /** Persiste token + rol en memoria y en la cookie. */
  function login(newToken: string, newRole: AuthRole): void {
    token.value = newToken
    role.value = newRole
    tokenCookie.value = newToken
    roleCookie.value = newRole
  }

  /** Limpia la sesión (memoria + cookie) y vuelve a /login. */
  async function logout(): Promise<void> {
    token.value = null
    role.value = null
    tokenCookie.value = null
    roleCookie.value = null
    await navigateTo('/login')
  }

  return { token, role, isAuthenticated, login, logout }
}
