import { computed, ref } from 'vue'
import {
  donorCentersService,
  type CenterDetailDTO
} from '~/services/donorCentersService'
import {
  donationService,
  type DonationDTO,
  type CreateDonationInput
} from '~/services/donationService'

/**
 * VIEW-MODEL — Puente reactivo del flujo de donación a un centro
 * (`/donor/donate/:centerId`).
 *
 * Es el ÚNICO punto que habla con `donorCentersService` y `donationService`.
 * Carga el detalle del centro, mantiene el mapa reactivo de cantidades que el
 * donante va ingresando, deriva qué ítems se donarán y orquesta el envío. Las
 * vistas solo consumen estado/derivados por props y emiten intenciones.
 *
 * Cada donación es independiente: el composable se instancia por `centerId`, de
 * modo que no se puede donar a dos centros en simultáneo desde un mismo flujo.
 */
export function useDonationViewModel(centerId: string) {
  const center = ref<CenterDetailDTO | null>(null)
  const donation = ref<DonationDTO | null>(null)
  /** Mapa needId → cantidad ingresada (0 = no seleccionado). */
  const quantities = ref<Record<string, number>>({})
  const isLoading = ref<boolean>(false)
  const isSubmitting = ref<boolean>(false)
  const error = ref<string | null>(null)
  const submitted = ref<boolean>(false)

  /** Necesidades del centro todavía activas: las únicas donables. */
  const activeNeeds = computed(() =>
    (center.value?.necesidades ?? []).filter((n) => n.estado === 'activa')
  )

  /**
   * Ítems que el donante realmente va a entregar: aquellos con cantidad >= 1.
   * Es la fuente del payload de creación.
   */
  const selectedItems = computed<{ needId: string; cantidad: number }[]>(() =>
    Object.entries(quantities.value)
      .filter(([, cantidad]) => cantidad >= 1)
      .map(([needId, cantidad]) => ({ needId, cantidad }))
  )

  /** Verdadero si hay al menos un ítem seleccionado. */
  const hasSelection = computed<boolean>(() => selectedItems.value.length > 0)

  /** Verdadero si se puede confirmar la donación en este momento. */
  const canSubmit = computed<boolean>(
    () => hasSelection.value && !isSubmitting.value && !submitted.value
  )

  /**
   * Carga el detalle del centro e inicializa el mapa de cantidades con todas
   * las necesidades activas en 0. Maneja loading y error de forma centralizada.
   */
  async function loadCenter(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const result = await donorCentersService.getCenterDetail(centerId)
      center.value = result
      quantities.value = Object.fromEntries(
        result.necesidades
          .filter((n) => n.estado === 'activa')
          .map((n) => [n.id, 0])
      )
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : 'No se pudo cargar el centro.'
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Crea la donación con los ítems seleccionados. Al completarse, guarda la
   * donación devuelta (con su código de seguimiento) y marca `submitted`.
   */
  async function submitDonation(): Promise<void> {
    if (!center.value) return
    isSubmitting.value = true
    error.value = null
    try {
      const input: CreateDonationInput = {
        centerId,
        centerNombre: center.value.nombre,
        items: selectedItems.value.map(({ needId, cantidad }) => {
          const need = center.value!.necesidades.find((n) => n.id === needId)!
          return {
            needId,
            needNombre: need.nombre,
            unidad: need.unidad,
            cantidad
          }
        })
      }
      donation.value = await donationService.createDonation(input)
      submitted.value = true
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : 'No se pudo registrar la donación.'
    } finally {
      isSubmitting.value = false
    }
  }

  /** Vuelve al detalle del centro de esta donación. */
  function goBack(): void {
    navigateTo('/donor/center/' + centerId)
  }

  /** Lleva al seguimiento de donaciones del donante. */
  function goTracking(): void {
    navigateTo('/donor/tracking')
  }

  return {
    // estado
    center,
    donation,
    quantities,
    isLoading,
    isSubmitting,
    error,
    submitted,
    // derivados
    activeNeeds,
    selectedItems,
    hasSelection,
    canSubmit,
    // acciones
    loadCenter,
    submitDonation,
    goBack,
    goTracking
  }
}
