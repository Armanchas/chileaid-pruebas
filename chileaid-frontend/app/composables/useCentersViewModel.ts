import { computed, ref } from 'vue'
import {
  donorCentersService,
  type CenterDTO,
  type CenterFilters,
  type EmergencyType
} from '~/services/donorCentersService'

/** Estado neutro de los filtros: muestra todos los centros sin restricción. */
const INITIAL_FILTERS: CenterFilters = {
  region: 'Todas las regiones',
  tipoEmergencia: 'todas'
}

/**
 * VIEW-MODEL — Puente reactivo del listado completo de centros (`/donor/centers`).
 *
 * Es el ÚNICO punto que habla con `donorCentersService`. Carga la colección
 * completa una sola vez y filtra en el cliente vía `computed`: al cambiar un
 * filtro no se vuelve a llamar al servicio. Los componentes solo consumen lo
 * que aquí se publica por props.
 */
export function useCentersViewModel() {
  const allCenters = ref<CenterDTO[]>([])
  const filters = ref<CenterFilters>({ ...INITIAL_FILTERS })
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // Filtro por emergencia (vínculo REAL centro↔emergencia = `emergenciaId`, la
  // FK del backend). Al llegar desde una emergencia del dashboard
  // (`?emergenciaId=…&emergenciaNombre=…`) se restringe a SUS centros. Antes se
  // filtraba por `region`+`tipo`, pero la `zona` de la emergencia (p. ej. "La
  // Araucanía") no coincide con la `region` del centro (p. ej. "Araucanía"), así
  // que no aparecía ningún centro.
  const emergenciaId = ref<string | null>(null)
  const emergenciaNombre = ref<string | null>(null)

  // Pre-aplica los filtros desde los query params de la URL. Se hace al
  // inicializar, antes de que la página llame a loadCenters(), para que el
  // primer render ya muestre los centros filtrados.
  const route = useRoute()
  if (typeof route.query.emergenciaId === 'string') {
    emergenciaId.value = route.query.emergenciaId
  }
  if (typeof route.query.emergenciaNombre === 'string') {
    emergenciaNombre.value = route.query.emergenciaNombre
  }
  // Deep-link opcional por región/tipo (independiente del filtro por emergencia).
  if (route.query.region) {
    filters.value.region = route.query.region as string
  }
  if (route.query.tipo) {
    filters.value.tipoEmergencia = route.query.tipo as EmergencyType
  }

  /**
   * Centros tras aplicar los filtros en AND. Los valores neutros
   * ('Todas las regiones' / 'todas') no restringen su dimensión; el filtro por
   * emergencia solo actúa si hay una emergencia seleccionada.
   */
  const filteredCenters = computed<CenterDTO[]>(() => {
    const { region, tipoEmergencia } = filters.value
    return allCenters.value.filter((center) => {
      const matchRegion =
        region === 'Todas las regiones' || center.region === region
      const matchTipo =
        tipoEmergencia === 'todas' || center.tipoEmergencia === tipoEmergencia
      const matchEmergencia =
        !emergenciaId.value || center.emergenciaId === emergenciaId.value
      return matchRegion && matchTipo && matchEmergencia
    })
  })

  /** Cantidad de centros visibles tras filtrar. */
  const totalVisible = computed<number>(() => filteredCenters.value.length)

  /** Verdadero si la combinación de filtros deja al menos un centro. */
  const hasResults = computed<boolean>(() => totalVisible.value > 0)

  /**
   * Carga la colección completa de centros. Maneja loading y error de forma
   * centralizada; el filtrado posterior es puramente reactivo.
   */
  async function loadCenters(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      allCenters.value = await donorCentersService.getAllCenters()
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : 'No se pudieron cargar los centros.'
    } finally {
      isLoading.value = false
    }
  }

  /** Actualiza el filtro de región. */
  function setRegion(region: string): void {
    filters.value.region = region
  }

  /** Actualiza el filtro de tipo de emergencia. */
  function setTipoEmergencia(tipo: 'todas' | EmergencyType): void {
    filters.value.tipoEmergencia = tipo
  }

  /** Quita el filtro por emergencia (vuelve a mostrar todos los centros). */
  function clearEmergencia(): void {
    emergenciaId.value = null
    emergenciaNombre.value = null
  }

  /** Vuelve los filtros al estado inicial (sin restricción). */
  function resetFilters(): void {
    filters.value = { ...INITIAL_FILTERS }
    clearEmergencia()
  }

  return {
    // estado
    allCenters,
    filters,
    emergenciaNombre,
    isLoading,
    error,
    // derivados
    filteredCenters,
    totalVisible,
    hasResults,
    // acciones
    loadCenters,
    setRegion,
    setTipoEmergencia,
    clearEmergencia,
    resetFilters
  }
}
