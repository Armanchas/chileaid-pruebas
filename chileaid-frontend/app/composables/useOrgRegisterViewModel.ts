import { computed, reactive, ref } from 'vue'
import {
  authService,
  type OrgRegisterPayload,
  type TipoCentro,
  type RegisterResult
} from '~/services/authService'
import { orgDocumentService } from '~/services/orgDocumentService'
import { resolveDocumentTipo } from '~/utils/documentType'
import { REGIONES_CHILE } from '~/services/donorDashboardService'

/** Largo mínimo de la contraseña (mismo criterio que el registro de donante). */
const MIN_PASSWORD = 6

/** Validación mínima de formato de correo, suficiente para el formulario. */
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

/**
 * Estado editable del formulario de registro de organización (CU-01).
 *
 * Misma forma que `OrgRegisterPayload` salvo que `tipoCentro` admite '' mientras
 * no se elige opción en el `<select>`; `rut` es opcional. Tres secciones:
 * datos de la organización · datos de contacto · credenciales; el documento de
 * respaldo se maneja aparte en `documentFile` (no viaja en `OrgRegisterPayload`).
 */
export interface OrgRegisterForm {
  // Datos de la organización
  nombre: string
  tipoCentro: TipoCentro | ''
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

/** Errores por campo: `null` cuando es válido o aún no fue tocado. */
export type OrgRegisterErrors = Record<string, string | null>

/**
 * VIEW-MODEL — Puente reactivo entre la vista de registro de organización (CU-01)
 * y el modelo.
 *
 * Es el ÚNICO punto de la app que habla con `authService.registerOrganization`.
 * Expone el estado del formulario como objeto compuesto (`form`), los errores por
 * campo en tiempo real (gated por `touched`), la validez global y las intenciones
 * de la vista. El componente OrgRegisterForm nunca toca el servicio: consume este
 * estado vía props desde la página y emite eventos.
 */
export function useOrgRegisterViewModel() {
  const form = reactive<OrgRegisterForm>({
    nombre: '',
    tipoCentro: '',
    rut: undefined,
    region: '',
    direccion: '',
    contactoNombre: '',
    email: '',
    telefono: '',
    password: '',
    confirmPassword: ''
  })

  /** Documento de respaldo (RF-03) adjuntado en el propio formulario de alta. */
  const documentFile = ref<File | null>(null)

  const isLoading = ref<boolean>(false)
  const submitError = ref<string | null>(null)
  const submitSuccess = ref<boolean>(false)

  /**
   * Flags de "campo tocado". El error de un campo solo se muestra una vez que el
   * usuario lo abandonó (evento `field-touch`) o tras intentar enviar.
   */
  const touched = reactive<Record<string, boolean>>({
    nombre: false,
    tipoCentro: false,
    region: false,
    direccion: false,
    contactoNombre: false,
    email: false,
    telefono: false,
    password: false,
    confirmPassword: false,
    document: false
  })

  // --- Validez individual de cada campo (independiente de `touched`) ---

  const isNombreValid = computed(() => form.nombre.trim().length > 0)
  const isTipoCentroValid = computed(() => form.tipoCentro !== '')
  const isRegionValid = computed(
    () =>
      form.region !== '' &&
      form.region !== 'Todas las regiones' &&
      REGIONES_CHILE.includes(form.region)
  )
  const isDireccionValid = computed(() => form.direccion.trim().length > 0)
  const isContactoNombreValid = computed(
    () => form.contactoNombre.trim().length > 0
  )
  const isEmailValid = computed(() => EMAIL_RE.test(form.email.trim()))
  const isTelefonoValid = computed(() => form.telefono.trim().length > 0)
  const isPasswordValid = computed(() => form.password.length >= MIN_PASSWORD)
  // confirmPassword es válido solo si tiene contenido y coincide con password.
  const isConfirmPasswordValid = computed(
    () => form.confirmPassword.length > 0 && form.confirmPassword === form.password
  )
  // Documento de respaldo obligatorio (PDF o JPG) para completar el alta.
  const isDocumentValid = computed(
    () => documentFile.value !== null && resolveDocumentTipo(documentFile.value.name) !== null
  )

  /** El formulario es válido cuando todos los campos requeridos pasan. */
  const isFormValid = computed(
    () =>
      isNombreValid.value &&
      isTipoCentroValid.value &&
      isRegionValid.value &&
      isDireccionValid.value &&
      isContactoNombreValid.value &&
      isEmailValid.value &&
      isTelefonoValid.value &&
      isPasswordValid.value &&
      isConfirmPasswordValid.value &&
      isDocumentValid.value
  )

  // --- Errores por campo en tiempo real (solo si el campo fue tocado) ---

  const errors = computed<OrgRegisterErrors>(() => ({
    nombre:
      touched.nombre && !isNombreValid.value
        ? 'Ingresa el nombre de la organización.'
        : null,
    tipoCentro:
      touched.tipoCentro && !isTipoCentroValid.value
        ? 'Indica qué función cumple.'
        : null,
    region:
      touched.region && !isRegionValid.value ? 'Selecciona una región.' : null,
    direccion:
      touched.direccion && !isDireccionValid.value
        ? 'Ingresa la dirección.'
        : null,
    contactoNombre:
      touched.contactoNombre && !isContactoNombreValid.value
        ? 'Ingresa el nombre de contacto.'
        : null,
    email:
      touched.email && !isEmailValid.value
        ? 'Ingresa un correo válido.'
        : null,
    telefono:
      touched.telefono && !isTelefonoValid.value
        ? 'Ingresa un teléfono de contacto.'
        : null,
    password:
      touched.password && !isPasswordValid.value
        ? `La contraseña debe tener al menos ${MIN_PASSWORD} caracteres.`
        : null,
    confirmPassword:
      touched.confirmPassword && !isConfirmPasswordValid.value
        ? 'Las contraseñas no coinciden.'
        : null,
    document:
      touched.document && !isDocumentValid.value
        ? documentFile.value
          ? 'Solo se aceptan archivos PDF o JPG.'
          : 'Adjunta tu documento de respaldo (PDF o JPG).'
        : null
  }))

  /** Marca un campo como tocado para activar su validación en tiempo real. */
  function onFieldTouch(field: string): void {
    touched[field] = true
  }

  /** Actualiza un campo del formulario (v-model compuesto, campo a campo). */
  function onUpdateModel(field: string, value: string): void {
    ;(form as Record<string, unknown>)[field] = value
  }

  /** Selección del documento de respaldo desde el `<input type="file">`. */
  function onDocumentChange(file: File | null): void {
    documentFile.value = file
    touched.document = true
  }

  /** Marca todos los campos como tocados (al intentar enviar inválido). */
  function touchAll(): void {
    Object.keys(touched).forEach((field) => {
      touched[field] = true
    })
  }

  /**
   * Envía la solicitud de verificación de la organización y, con el JWT que
   * devuelve el alta, sube de inmediato el documento de respaldo (mismo
   * flujo de presigned URL en dos pasos que usa el perfil, ver
   * `useOrgDocumentsViewModel`).
   *
   * La cuenta se crea igual aunque la subida del documento falle (network
   * error, S3 caído, etc.): no tiene sentido descartar un email/rut ya
   * validado por un problema de storage. En ese caso se navega con
   * `docPending=1` para que el login avise que el documento quedó pendiente
   * de subir desde el perfil. La org sigue "Pendiente" hasta la aprobación
   * del admin — el token solo habilita la subida, no cambia ese estado.
   */
  async function submit(): Promise<void> {
    touchAll()
    if (!isFormValid.value || isLoading.value) return

    isLoading.value = true
    submitError.value = null

    try {
      const payload: OrgRegisterPayload = {
        nombre: form.nombre.trim(),
        tipoCentro: form.tipoCentro as TipoCentro,
        rut: form.rut?.trim() || undefined,
        region: form.region,
        direccion: form.direccion.trim(),
        contactoNombre: form.contactoNombre.trim(),
        email: form.email.trim(),
        telefono: form.telefono.trim(),
        password: form.password,
        confirmPassword: form.confirmPassword
      }

      const result: RegisterResult =
        await authService.registerOrganization(payload)

      if (!result.success) {
        submitError.value = result.error ?? 'No se pudo enviar la solicitud.'
        return
      }

      let docPending = false
      const file = documentFile.value
      const tipo = file ? resolveDocumentTipo(file.name) : null
      if (result.token && file && tipo) {
        try {
          const { presignedPost, objectKey } = await orgDocumentService.getUploadUrl(
            file.name,
            tipo,
            result.token
          )
          await orgDocumentService.uploadToS3(presignedPost, file)
          await orgDocumentService.saveDocument(file.name, objectKey, tipo, result.token)
        } catch {
          docPending = true
        }
      }

      submitSuccess.value = true
      navigateTo(`/login?registered=org${docPending ? '&docPending=1' : ''}`)
    } catch (e) {
      submitError.value =
        e instanceof Error ? e.message : 'No se pudo enviar la solicitud.'
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
    form,
    documentFile,
    errors,
    touched,
    isLoading,
    submitError,
    submitSuccess,
    isFormValid,
    // acciones
    onFieldTouch,
    onUpdateModel,
    onDocumentChange,
    submit,
    onGoToLogin
  }
}
