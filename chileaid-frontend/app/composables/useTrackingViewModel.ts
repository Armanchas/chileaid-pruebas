import { computed, ref } from 'vue'
import {
  donationService,
  type DonationDTO
} from '~/services/donationService'

/** Donaciones por página en el historial. */
const PAGE_SIZE = 10

/**
 * VIEW-MODEL — Puente reactivo del historial de donaciones (`/donor/tracking`).
 *
 * Es el ÚNICO punto que habla con `donationService`. Carga la página actual
 * server-side (`GET /donations?limit=&offset=`): cambiar de página vuelve a
 * llamar al servicio en vez de re-cortar un array ya traído completo. También
 * gobierna el modal de QR. Las vistas solo consumen estado/derivados por props
 * y emiten intenciones.
 */
export function useTrackingViewModel() {
  const donations = ref<DonationDTO[]>([])
  const total = ref<number>(0)
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)
  const activeQRCode = ref<string | null>(null)
  const currentPage = ref<number>(1)
  // Id de la donación que se está cancelando (deshabilita esa fila mientras corre).
  const cancellingId = ref<string | null>(null)

  /** Número total de páginas según el conteo del backend. */
  const totalPages = computed<number>(() =>
    Math.max(1, Math.ceil(total.value / PAGE_SIZE))
  )

  /** Verdadero si existe una página siguiente. */
  const hasNextPage = computed<boolean>(
    () => currentPage.value < totalPages.value
  )

  /** Verdadero si existe una página anterior. */
  const hasPrevPage = computed<boolean>(() => currentPage.value > 1)

  /**
   * Carga la página actual del historial de donaciones del donante. Maneja
   * loading y error de forma centralizada.
   */
  async function loadDonations(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const pagina = await donationService.getMyDonations({
        limit: PAGE_SIZE,
        offset: (currentPage.value - 1) * PAGE_SIZE
      })
      donations.value = pagina.items
      total.value = pagina.total
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : 'No se pudieron cargar las donaciones.'
    } finally {
      isLoading.value = false
    }
  }

  /** Avanza a la página siguiente si la hay. */
  function nextPage(): void {
    if (!hasNextPage.value) return
    currentPage.value++
    loadDonations()
  }

  /** Retrocede a la página anterior si la hay. */
  function prevPage(): void {
    if (!hasPrevPage.value) return
    currentPage.value--
    loadDonations()
  }

  /**
   * Cancela una donación pendiente (`POST /donations/{id}/cancel`) y reemplaza
   * el ítem en el estado local con el DTO devuelto (ya en estado `cancelada`),
   * sin recargar toda la lista. Un 404/409 se muestra en `error`.
   */
  async function cancelDonation(id: string): Promise<void> {
    cancellingId.value = id
    error.value = null
    try {
      const updated = await donationService.cancelDonation(id)
      const idx = donations.value.findIndex((d) => d.id === id)
      if (idx !== -1) donations.value[idx] = updated
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : 'No se pudo cancelar la donación.'
    } finally {
      cancellingId.value = null
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

  /** Vuelve a la página de perfil. */
  function goProfile(): void {
    navigateTo('/donor/profile')
  }

  return {
    // estado
    donations,
    total,
    isLoading,
    error,
    activeQRCode,
    currentPage,
    cancellingId,
    // derivados
    totalPages,
    hasNextPage,
    hasPrevPage,
    // acciones
    loadDonations,
    nextPage,
    prevPage,
    cancelDonation,
    openQR,
    closeQR,
    goProfile
  }
}
