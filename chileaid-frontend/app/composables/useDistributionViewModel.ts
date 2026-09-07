import { computed, ref } from 'vue'
import {
  distributionService,
  type DistributionLotDTO,
  type StockItem,
  type CreateLotInput,
  type LotSalida,
  type OrgType
} from '~/services/distributionService'
import { orgProfileService } from '~/services/orgProfileService'

/**
 * VIEW-MODEL — Puente reactivo entre la distribución de lotes de la organización
 * y el modelo.
 *
 * Es el ÚNICO punto de la app que habla con `distributionService`. Expone estado
 * reactivo (ref/computed) y las intenciones (`loadData`, abrir/cerrar el modal,
 * `submitLot`); los componentes nunca tocan el servicio, solo consumen lo que
 * aquí se publica vía props desde la página.
 *
 * `accionesDisponibles` traduce el tipo de centro a las salidas que puede hacer:
 * regla de presentación derivada del dominio, centralizada aquí.
 */
export function useDistributionViewModel() {
  const lots = ref<DistributionLotDTO[]>([])
  const stock = ref<StockItem[]>([])
  const isLoading = ref<boolean>(false)
  const isSubmitting = ref<boolean>(false)
  const error = ref<string | null>(null)
  const submitError = ref<string | null>(null)
  const showCreateModal = ref<boolean>(false)
  // Tipo de centro de la org (del perfil): decide las salidas disponibles.
  const orgTipo = ref<OrgType>('ambos')

  /** Total de unidades distribuidas (suma de las cantidades de todos los lotes). */
  const totalDistribuido = computed<number>(() =>
    lots.value.reduce((sum, lot) => sum + lot.cantidad, 0)
  )

  /** Salidas disponibles según el tipo de centro cargado del perfil. */
  const availableActions = computed<LotSalida[]>(() =>
    accionesDisponibles(orgTipo.value)
  )

  /**
   * Carga en paralelo los lotes y el stock disponible. Maneja los estados de
   * carga y error de forma centralizada.
   */
  async function loadData(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const [lotsData, stockData, profile] = await Promise.all([
        distributionService.getLots(),
        distributionService.getStock(),
        // Solo para derivar las salidas disponibles; si falla, cae a 'ambos'.
        orgProfileService.getOrgProfile().catch(() => null)
      ])
      lots.value = lotsData
      stock.value = stockData
      if (profile) orgTipo.value = profile.tipo
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : 'No se pudieron cargar los datos de distribución.'
    } finally {
      isLoading.value = false
    }
  }

  /** Abre el modal de creación de lote (limpia el error previo del formulario). */
  function openCreateModal(): void {
    submitError.value = null
    showCreateModal.value = true
  }

  /** Cierra el modal de creación de lote. */
  function closeCreateModal(): void {
    showCreateModal.value = false
  }

  /**
   * Registra una nueva salida de stock. En éxito recarga los datos y cierra el
   * modal; en error (p. ej. `Stock insuficiente`) expone el mensaje sin cerrar.
   */
  async function submitLot(input: CreateLotInput): Promise<void> {
    if (isSubmitting.value) return

    isSubmitting.value = true
    submitError.value = null
    try {
      await distributionService.createLot(input)
      await loadData()
      closeCreateModal()
    } catch (e) {
      submitError.value =
        e instanceof Error ? e.message : 'No se pudo registrar la salida.'
    } finally {
      isSubmitting.value = false
    }
  }

  /**
   * Salidas disponibles según el tipo de centro:
   *  - `centro_acopio`      → solo envío a terreno
   *  - `punto_distribucion` → solo entrega a beneficiario
   *  - `ambos`              → ambas
   */
  function accionesDisponibles(orgTipo: OrgType): LotSalida[] {
    switch (orgTipo) {
      case 'centro_acopio':
        return ['enviado_a_terreno']
      case 'punto_distribucion':
        return ['entregado_a_beneficiario']
      case 'ambos':
        return ['enviado_a_terreno', 'entregado_a_beneficiario']
    }
  }

  return {
    // estado
    lots,
    stock,
    isLoading,
    isSubmitting,
    error,
    submitError,
    showCreateModal,
    orgTipo,
    // derivados
    totalDistribuido,
    availableActions,
    // acciones
    loadData,
    openCreateModal,
    closeCreateModal,
    submitLot,
    accionesDisponibles
  }
}
