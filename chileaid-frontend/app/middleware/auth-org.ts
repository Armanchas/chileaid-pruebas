/**
 * Middleware de ruta — Protege las páginas de la organización receptora (`/org/*`).
 * Exige sesión activa con rol `org`; en caso contrario redirige a /login
 * guardando la ruta destino en `?redirect=` (tras autenticar se vuelve a ella).
 */
export default defineNuxtRouteMiddleware((to) => {
  const { isAuthenticated, role } = useAuth()
  if (!isAuthenticated.value || role.value !== 'org') {
    return navigateTo('/login?redirect=' + encodeURIComponent(to.fullPath))
  }
})
