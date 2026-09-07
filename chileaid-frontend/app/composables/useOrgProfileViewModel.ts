import { computed, reactive, ref } from 'vue'
import {
  orgProfileService,
  type OrgProfileDTO,
  type OrgType,
  type OrgEstado
} from '~/services/orgProfileService'

/**
 * VIEW-MODEL — Puente reactivo del perfil de la organización (`/org/profile`).
 *
 * Es el ÚNICO punto que habla con `orgProfileService`. Carga el perfil, mantiene
 * el formulario de los datos de contacto editables y orquesta el guardado. Las
 * vistas solo consumen estado/derivados por props y emiten intenciones. El mapeo
 * de etiquetas/colores de `tipo` y `estado` es presentación derivada, no datos.
 */
export function useOrgProfileViewModel() {
  const profile = ref<OrgProfileDTO | null>(null)

  // formulario de edición (solo datos de contacto)
  const form = reactive<{
    contactoNombre: string
    email: string
    telefono: string
    region: string
  }>({
    contactoNombre: '',
    email: '',
    telefono: '',
    region: ''
  })

  // carga general
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // guardado
  const isSaving = ref<boolean>(false)
  const saveError = ref<string | null>(null)
  const saveSuccess = ref<boolean>(false)

  /** Etiqueta legible en español de la función de la organización. */
  const labelTipo = computed<string>(() => {
    const labels: Record<OrgType, string> = {
      centro_acopio: 'Centro de acopio',
      punto_distribucion: 'Punto de distribución',
      ambos: 'Acopio y distribución'
    }
    return profile.value ? labels[profile.value.tipo] : ''
  })

  /** Etiqueta legible en español del estado de verificación. */
  const labelEstado = computed<string>(() => {
    const labels: Record<OrgEstado, string> = {
      pendiente: 'Pendiente de verificación',
      activa: 'Activa',
      rechazada: 'Rechazada',
      inactiva: 'Inactiva'
    }
    return profile.value ? labels[profile.value.estado] : ''
  })

  /** Clases del badge de estado (color según verificación). */
  const colorEstado = computed<string>(() => {
    const colors: Record<OrgEstado, string> = {
      activa: 'bg-green-100 text-green-700',
      pendiente: 'bg-amber-100 text-amber-700',
      rechazada: 'bg-red-100 text-red-700',
      inactiva: 'bg-slate-100 text-slate-500'
    }
    return profile.value ? colors[profile.value.estado] : ''
  })

  /** `true` si el formulario difiere del perfil cargado en algún campo editable. */
  const isFormDirty = computed<boolean>(() => {
    if (!profile.value) return false
    return (
      form.contactoNombre !== profile.value.contactoNombre ||
      form.email !== profile.value.email ||
      form.telefono !== profile.value.telefono ||
      form.region !== profile.value.region
    )
  })

  /** Vuelca los datos de contacto del perfil en el formulario reactivo. */
  function syncForm(source: OrgProfileDTO): void {
    form.contactoNombre = source.contactoNombre
    form.email = source.email
    form.telefono = source.telefono
    form.region = source.region
  }

  /**
   * Carga el perfil de la organización e inicializa el formulario con los datos
   * de contacto recibidos. Maneja loading y error centralizados.
   */
  async function loadProfile(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const result = await orgProfileService.getOrgProfile()
      profile.value = result
      syncForm(result)
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : 'No se pudo cargar el perfil.'
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Guarda los cambios del formulario. En éxito actualiza el perfil y muestra
   * un feedback efímero (3s); en validación fallida expone el error del service.
   */
  async function saveProfile(): Promise<void> {
    isSaving.value = true
    saveError.value = null
    saveSuccess.value = false
    try {
      const result = await orgProfileService.updateOrgProfile({
        contactoNombre: form.contactoNombre,
        email: form.email,
        telefono: form.telefono,
        region: form.region
      })
      if (result.success && result.profile) {
        profile.value = result.profile
        syncForm(result.profile)
        saveSuccess.value = true
        setTimeout(() => {
          saveSuccess.value = false
        }, 3000)
      } else {
        saveError.value = result.error ?? 'No se pudieron guardar los cambios.'
      }
    } catch (e) {
      saveError.value =
        e instanceof Error ? e.message : 'No se pudieron guardar los cambios.'
    } finally {
      isSaving.value = false
    }
  }

  /** Descarta los cambios y vuelve el formulario a los valores del perfil. */
  function resetForm(): void {
    if (profile.value) syncForm(profile.value)
    saveError.value = null
  }

  /** Vuelve al panel de la organización. */
  function goBack(): void {
    navigateTo('/org')
  }

  return {
    // estado
    profile,
    form,
    isLoading,
    error,
    isSaving,
    saveError,
    saveSuccess,
    // derivados
    labelTipo,
    labelEstado,
    colorEstado,
    isFormDirty,
    // acciones
    loadProfile,
    saveProfile,
    resetForm,
    goBack
  }
}
