import { computed, reactive, ref } from 'vue'
import {
  authService,
  type DonorRegisterData,
  type RegisterResult
} from '~/services/authService'

/** Campos del formulario, usados como clave de los flags `touched`. */
type DonorField = 'nombre' | 'apellido' | 'email' | 'password' | 'confirmPassword'

/** Validación mínima de formato de correo, suficiente para el mock. */
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

/**
 * VIEW-MODEL — Puente reactivo entre la vista de registro de donante y el
 * modelo.
 *
 * Es el ÚNICO punto de la app que habla con `authService.registerDonor`.
 * Expone estado reactivo (ref/computed), los errores por campo en tiempo real
 * y las intenciones de la vista. El componente DonorRegisterForm nunca toca el
 * servicio: solo consume este estado vía props desde la página y emite eventos.
 */
export function useDonorRegisterViewModel() {
  const { login } = useAuth()

  const nombre = ref<string>('')
  const apellido = ref<string>('')
  const email = ref<string>('')
  const password = ref<string>('')
  const confirmPassword = ref<string>('')

  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  /**
   * Flags de "campo tocado". Viven dentro del ViewModel: el error de un campo
   * solo se muestra una vez que el usuario lo abandonó (evento `field-touched`).
   */
  const touched = reactive<Record<DonorField, boolean>>({
    nombre: false,
    apellido: false,
    email: false,
    password: false,
    confirmPassword: false
  })

  // --- Validez individual de cada campo (independiente de `touched`) ---

  const isNombreValid = computed(() => nombre.value.trim().length >= 2)
  const isApellidoValid = computed(() => apellido.value.trim().length >= 2)
  const isEmailValid = computed(() => EMAIL_RE.test(email.value.trim()))
  const isPasswordValid = computed(() => password.value.length >= 6)
  const isConfirmPasswordValid = computed(() => confirmPassword.value === password.value && confirmPassword.value.length >= 6)

  /** El formulario es válido cuando todos los campos pasan su validación. */
  const isFormValid = computed(
    () =>
      isNombreValid.value &&
      isApellidoValid.value &&
      isEmailValid.value &&
      isPasswordValid.value &&
      isConfirmPasswordValid.value
  )

  // --- Errores por campo: null si es válido o aún no fue tocado ---

  const nombreError = computed(() =>
    touched.nombre && !isNombreValid.value
      ? 'Ingresa tu nombre (mínimo 2 caracteres).'
      : null
  )
  const apellidoError = computed(() =>
    touched.apellido && !isApellidoValid.value
      ? 'Ingresa tu apellido (mínimo 2 caracteres).'
      : null
  )
  const emailError = computed(() =>
    touched.email && !isEmailValid.value
      ? 'Ingresa un correo electrónico válido.'
      : null
  )
  const passwordError = computed(() =>
    touched.password && !isPasswordValid.value
      ? 'La contraseña debe tener al menos 6 caracteres.'
      : null
  )
  const confirmPasswordError = computed(() =>
    touched.confirmPassword && !isConfirmPasswordValid.value
      ? 'Las contraseñas no coinciden.'
      : null
  )

  /** Marca un campo como tocado para activar su validación en tiempo real. */
  function onFieldTouched(field: DonorField): void {
    touched[field] = true
  }

  /** Restablece el formulario a su estado inicial. */
  function resetForm(): void {
    nombre.value = ''
    apellido.value = ''
    email.value = ''
    password.value = ''
    confirmPassword.value = ''
    touched.nombre = false
    touched.apellido = false
    touched.email = false
    touched.password = false
    touched.confirmPassword = false
  }

  async function onSubmit(payload?: DonorRegisterData): Promise<void> {
    if (payload) {
      nombre.value = payload.nombre
      apellido.value = payload.apellido
      email.value = payload.email
      password.value = payload.password
      confirmPassword.value = payload.confirmPassword
    }

    if (!isFormValid.value || isLoading.value) return

    isLoading.value = true
    error.value = null

    try {
      const result: RegisterResult = await authService.registerDonor({
        nombre: nombre.value,
        apellido: apellido.value,
        email: email.value,
        password: password.value,
        confirmPassword: confirmPassword.value
      })

      if (result.success && result.token) {
        login(result.token, 'donor')
        await navigateTo('/donor')
      } else {
        error.value = result.error ?? 'No se pudo completar el registro.'
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'No se pudo completar el registro.'
    } finally {
      isLoading.value = false
    }
  }

  /** Navega a la página de inicio de sesión. */
  function onGoToLogin(): void {
    navigateTo('/login')
  }

  return {
    // estado
    nombre,
    apellido,
    email,
    password,
    confirmPassword,
    isLoading,
    error,
    isFormValid,
    // errores por campo
    nombreError,
    apellidoError,
    emailError,
    passwordError,
    confirmPasswordError,
    // acciones
    onFieldTouched,
    onSubmit,
    onGoToLogin
  }
}
