/**
 * Middleware de ruta — Protege las páginas de administración (`/admin/*`). Exige
 * sesión activa con rol `admin`; en caso contrario redirige a /login guardando la
 * ruta destino en `?redirect=` (tras autenticar se vuelve a ella).
 */
export default defineNuxtRouteMiddleware((to) => {
  const { isAuthenticated, role } = useAuth()
  if (!isAuthenticated.value || role.value !== 'admin') {
    return navigateTo('/login?redirect=' + encodeURIComponent(to.fullPath))
  }
})
