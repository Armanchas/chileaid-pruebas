import { computed, ref } from 'vue'
import { authService, type AuthResult, type AuthRole } from '~/services/authService'

/** Área de inicio de cada rol tras autenticarse. */
const ROUTE_BY_ROLE: Record<AuthRole, string> = {
  donor: '/donor',
  org: '/org',
  admin: '/admin'
}

/**
 * Valida el `?redirect=` de la query. Solo acepta rutas internas relativas —
 * empiezan con una sola `/` (no `//`, que el navegador interpreta como URL
 * absoluta a otro host) — para evitar un open-redirect. Si no es válido,
 * devuelve `null` y el login cae al home del rol.
 */
function safeRedirect(value: unknown): string | null {
  return typeof value === 'string' &&
    value.startsWith('/') &&
    !value.startsWith('//')
    ? value
    : null
}

/**
 * VIEW-MODEL — Puente reactivo entre la vista de login y el modelo.
 *
 * Es el ÚNICO punto de la app que habla con `authService`. Expone estado
 * reactivo (ref/computed) y la intención `onSubmit`; el componente LoginForm
 * nunca toca el servicio, solo consume este estado vía props desde la página.
 */
export function useLoginViewModel() {
  const { login } = useAuth()
  const route = useRoute()

  const email = ref('')
  const password = ref('')
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  /** El formulario es válido con un email no vacío y password de 6+ caracteres. */
  const isFormValid = computed(
    () => email.value.trim().length > 0 && password.value.length >= 6
  )

  /**
   * Intenta autenticar con las credenciales actuales.
   *
   * Acepta opcionalmente las credenciales emitidas por la vista; si no llegan,
   * usa el estado interno. Por ahora solo registra el resultado en consola,
   * listo para cablear a `useRouter().push()` y a la persistencia de sesión.
   */
  async function onSubmit(credentials?: { email: string; password: string }): Promise<void> {
    if (credentials) {
      email.value = credentials.email
      password.value = credentials.password
    }

    if (!isFormValid.value || isLoading.value) return

    isLoading.value = true
    error.value = null

    try {
      const result: AuthResult = await authService.login({
        email: email.value,
        password: password.value
      })

      if (result.success && result.token && result.role) {
        // Persistimos la sesión y navegamos: si venimos de una ruta protegida
        // (login diferido, p. ej. "Donar" desde el mapa público), volvemos a esa
        // ruta vía `?redirect=`; si no, al home del rol. El destino de la ruta
        // protegida se re-valida por su propio middleware según el rol.
        login(result.token, result.role)
        await navigateTo(
          safeRedirect(route.query.redirect) ?? ROUTE_BY_ROLE[result.role]
        )
      } else {
        error.value = result.error ?? 'No se pudo iniciar sesión.'
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'No se pudo iniciar sesión.'
    } finally {
      isLoading.value = false
    }
  }

  // --- Intenciones secundarias (placeholder hasta tener rutas/API) ---

  function onDonorAccess(): void {
    navigateTo('/register/donor')
  }

  function onOrgAccess(): void {
    navigateTo('/register/org')
  }

  return {
    // estado
    email,
    password,
    isLoading,
    error,
    isFormValid,
    // acciones
    onSubmit,
    onDonorAccess,
    onOrgAccess
  }
}
