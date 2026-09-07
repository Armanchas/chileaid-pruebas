import { computed, ref } from 'vue'
import {
  donorCentersService,
  type CenterDetailDTO,
  type NeedDTO
} from '~/services/donorCentersService'

/**
 * VIEW-MODEL — Puente reactivo del detalle de un centro (`/donor/center/:id`).
 *
 * Es el ÚNICO punto que habla con `donorCentersService`. Expone el centro
 * cargado, los estados de carga/error y los derivados que segmentan las
 * necesidades (urgentes / otras / completadas) para que las vistas solo
 * consuman listas ya filtradas vía props.
 */
export function useCenterDetailViewModel() {
  const center = ref<CenterDetailDTO | null>(null)
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  /** Necesidades urgentes y todavía activas: se destacan en tarjetas. */
  const urgentNeeds = computed<NeedDTO[]>(() =>
    (center.value?.necesidades ?? []).filter(
      (n) => n.urgente && n.estado === 'activa'
    )
  )

  /** Necesidades no urgentes y activas: requerimientos continuos. */
  const otherNeeds = computed<NeedDTO[]>(() =>
    (center.value?.necesidades ?? []).filter(
      (n) => !n.urgente && n.estado === 'activa'
    )
  )

  /** Necesidades cuya meta ya se cumplió. */
  const completedNeeds = computed<NeedDTO[]>(() =>
    (center.value?.necesidades ?? []).filter((n) => n.estado === 'completada')
  )

  /** Verdadero si el centro está cerrado (no recibe más donaciones). */
  const isClosed = computed<boolean>(() => center.value?.estado === 'cerrado')

  /**
   * Carga el detalle del centro indicado. Maneja loading y error de forma
   * centralizada.
   */
  async function loadCenter(id: string): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      center.value = await donorCentersService.getCenterDetail(id)
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : 'No se pudo cargar el centro.'
    } finally {
      isLoading.value = false
    }
  }

  return {
    // estado
    center,
    isLoading,
    error,
    // derivados
    urgentNeeds,
    otherNeeds,
    completedNeeds,
    isClosed,
    // acciones
    loadCenter
  }
}
