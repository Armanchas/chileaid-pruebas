/**
 * Middleware de ruta — Protege las páginas del donante (`/donor/*`). Exige sesión
 * activa con rol `donor`; en caso contrario redirige a /login guardando la ruta
 * destino en `?redirect=` (login diferido: tras autenticar se vuelve a ella).
 * Habilita el flujo "ver el mapa público → Donar → login → volver a donar".
 */
export default defineNuxtRouteMiddleware((to) => {
  const { isAuthenticated, role } = useAuth()
  if (!isAuthenticated.value || role.value !== 'donor') {
    return navigateTo('/login?redirect=' + encodeURIComponent(to.fullPath))
  }
})
