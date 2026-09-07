import { authService } from '~/services/authService'

/**
 * PLUGIN — Rehidrata la sesión desde `GET /auth/me` al cargar/recargar la app
 * (§1.7 / §2.2).
 *
 * `useAuth().role` se siembra al hacer login desde un decode client-side del
 * JWT (`utils/jwt.ts`) que NO valida la firma — un token manipulado podría
 * alterar el `role` percibido por la UI. Este plugin corre una única vez por
 * carga completa (SSR o boot del cliente, no en cada navegación SPA — para eso
 * están los middlewares `auth-*`) y, si hay sesión, le pide al backend la
 * verdad server-side. Si el rol servido difiere del decodificado, gana el del
 * backend. Si la request falla por una razón que NO sea el 401 por token
 * inválido (`apiFetch` ya cierra sesión en ese caso), el decode local se deja
 * como estaba: es solo la verdad optimista, no se fuerza un logout por un
 * error transitorio (p. ej. red caída).
 */
export default defineNuxtPlugin(async () => {
  const { token, role, login } = useAuth()
  const currentToken = token.value
  if (!currentToken) return

  const me = await authService.getMe()
  if (me && me.role !== role.value) {
    login(currentToken, me.role)
  }
})
