import { computed, ref } from 'vue'
import {
  donorCentersService,
  type CenterDTO,
  type EmergencyDTO
} from '~/services/donorCentersService'

/**
 * VIEW-MODEL — Puente reactivo entre el panel del donante y el modelo.
 *
 * Es el ÚNICO punto de la app que habla con `donorCentersService`. Expone
 * estado reactivo (ref/computed) y la intención `loadDashboard`; los
 * componentes nunca tocan el servicio, solo consumen lo que aquí se publica
 * vía props desde la página.
 */
export function useDonorDashboardViewModel() {
  const emergencies = ref<EmergencyDTO[]>([])
  const criticalCenters = ref<CenterDTO[]>([])
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  /** Cantidad de emergencias en estado 'activa'. */
  const activeEmergenciesCount = computed(
    () => emergencies.value.filter((e) => e.estado === 'activa').length
  )

  /** Verdadero si algún centro está en estado 'critico'. */
  const hasCriticalCenters = computed(() =>
    criticalCenters.value.some((c) => c.estado === 'critico')
  )

  /**
   * Carga en paralelo las emergencias activas y los centros más urgentes.
   * Maneja los estados de carga y error de forma centralizada.
   */
  async function loadDashboard(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const [emergenciesData, centersData] = await Promise.all([
        donorCentersService.getActiveEmergencies(),
        donorCentersService.getCriticalCenters()
      ])
      emergencies.value = emergenciesData
      criticalCenters.value = centersData
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'No se pudo cargar el panel.'
    } finally {
      isLoading.value = false
    }
  }

  return {
    // estado
    emergencies,
    criticalCenters,
    isLoading,
    error,
    // derivados
    activeEmergenciesCount,
    hasCriticalCenters,
    // acciones
    loadDashboard
  }
}
