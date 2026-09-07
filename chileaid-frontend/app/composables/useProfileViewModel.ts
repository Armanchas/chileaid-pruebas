import { computed, ref } from 'vue'
import {
  profileService,
  type DonorProfileDTO
} from '~/services/profileService'
import {
  donationService,
  type DonationDTO
} from '~/services/donationService'

/**
 * VIEW-MODEL — Puente reactivo del perfil del donante (`/donor/profile`).
 *
 * Es el ÚNICO punto que habla con `profileService` y `donationService`. Carga en
 * paralelo el perfil y el historial de donaciones, mantiene el formulario de
 * edición y orquesta el guardado y el modal de QR. Las vistas solo consumen
 * estado/derivados por props y emiten intenciones.
 */
/** Cuántas donaciones recientes se muestran en el resumen del perfil. */
const RECENT_DONATIONS_LIMIT = 5

export function useProfileViewModel() {
  const profile = ref<DonorProfileDTO | null>(null)
  const donations = ref<DonationDTO[]>([])
  const totalDonaciones = ref<number>(0)

  // formulario de edición
  const form = ref<{ nombre: string; apellido: string; email: string }>({
    nombre: '',
    apellido: '',
    email: ''
  })
  const isSaving = ref<boolean>(false)
  const saveSuccess = ref<boolean>(false)
  const saveError = ref<string | null>(null)

  // modal QR: codigoSeguimiento de la donación seleccionada (null = cerrado)
  const activeQRCode = ref<string | null>(null)

  // carga general
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  /** Donación más reciente (la primera de la lista), o null si no hay. */
  const lastDonation = computed<DonationDTO | null>(() =>
    donations.value.length > 0 ? donations.value[0] : null
  )

  /** Las donaciones más recientes: vista resumida en el perfil (ya vienen acotadas). */
  const recentDonations = computed<DonationDTO[]>(() => donations.value)

  /**
   * Carga en paralelo el perfil y las donaciones más recientes del donante (solo
   * las `RECENT_DONATIONS_LIMIT` necesarias para el resumen, no todo el
   * historial — eso vive en `/donor/tracking`), e inicializa el formulario con
   * los datos del perfil. Maneja loading y error centralizados.
   */
  async function loadProfile(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const [profileResult, donationsResult] = await Promise.all([
        profileService.getProfile(),
        donationService.getMyDonations({ limit: RECENT_DONATIONS_LIMIT, offset: 0 })
      ])
      profile.value = profileResult
      donations.value = donationsResult.items
      totalDonaciones.value = donationsResult.total
      form.value = {
        nombre: profileResult.nombre,
        apellido: profileResult.apellido,
        email: profileResult.email
      }
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
      const result = await profileService.updateProfile(form.value)
      if (result.success && result.profile) {
        profile.value = result.profile
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

  /** Abre el modal de QR con el código de la donación seleccionada. */
  function openQR(codigoSeguimiento: string): void {
    activeQRCode.value = codigoSeguimiento
  }

  /** Cierra el modal de QR. */
  function closeQR(): void {
    activeQRCode.value = null
  }

  /** Vuelve al panel del donante. */
  function goBack(): void {
    navigateTo('/donor')
  }

  return {
    // estado
    profile,
    donations,
    totalDonaciones,
    form,
    isSaving,
    saveSuccess,
    saveError,
    activeQRCode,
    isLoading,
    error,
    // derivados
    lastDonation,
    recentDonations,
    // acciones
    loadProfile,
    saveProfile,
    openQR,
    closeQR,
    goBack
  }
}
