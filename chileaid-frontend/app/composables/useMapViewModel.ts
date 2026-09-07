import { computed, ref } from 'vue'
import {
  donorCentersService,
  type CenterDTO
} from '~/services/donorCentersService'

/** Opciones del ViewModel del mapa. */
export interface MapViewModelOptions {
  /**
   * Centro a preseleccionar. Llega como query param `?center=...` cuando se
   * navega desde el detalle de un centro: tras cargar, abre ese centro.
   */
  initialCenterId?: string
  /**
   * Ruta a la que vuelve el botón "Volver". El mapa se monta en dos contextos:
   * `/donor/map` (donante autenticado, vuelve a `/donor`, valor por defecto) y
   * `/map` (mapa público de la landing, vuelve a `/`).
   */
  backTo?: string
}

/**
 * VIEW-MODEL — Puente reactivo del mapa de centros de acopio.
 *
 * Es el ÚNICO punto que habla con `donorCentersService`. Carga la colección
 * completa de centros (endpoint público `GET /centers`), gobierna cuál tiene el
 * panel de detalle abierto y decide la navegación. La vista solo consume
 * estado/derivados por props y emite intenciones; nunca toca el servicio ni
 * Leaflet a través de aquí.
 *
 * Se reutiliza tal cual en el mapa del donante (`/donor/map`) y en el mapa
 * público (`/map`): la única diferencia de comportamiento es `backTo`. El login
 * diferido lo resuelve el middleware `auth-donor` de las rutas `/donor/*` a las
 * que navegan `donate`/`goToCenter`: si el visitante es anónimo, lo desvía a
 * `/login?redirect=...` y lo devuelve tras autenticar.
 */
export function useMapViewModel(options: MapViewModelOptions = {}) {
  const { initialCenterId, backTo = '/donor' } = options
  const centers = ref<CenterDTO[]>([])
  /** Centro cuyo panel de detalle está abierto (null = ninguno). */
  const selectedCenter = ref<CenterDTO | null>(null)
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  /** Centros en estado crítico (los que pulsan en el mapa). */
  const criticalCenters = computed<CenterDTO[]>(() =>
    centers.value.filter((c) => c.estado === 'critico')
  )

  /** Cantidad total de centros cargados. */
  const totalCenters = computed<number>(() => centers.value.length)

  /**
   * Carga todos los centros. Si llegó un `initialCenterId`, deja ese centro
   * preseleccionado para centrar el mapa en él. Maneja loading y error de forma
   * centralizada.
   */
  async function loadCenters(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      centers.value = await donorCentersService.getAllCenters()
      if (initialCenterId) {
        selectedCenter.value =
          centers.value.find((c) => c.id === initialCenterId) ?? null
      }
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : 'No se pudieron cargar los centros.'
    } finally {
      isLoading.value = false
    }
  }

  /** Abre el panel de detalle del centro indicado. */
  function selectCenter(center: CenterDTO): void {
    selectedCenter.value = center
  }

  /** Cierra el panel de detalle. */
  function clearSelection(): void {
    selectedCenter.value = null
  }

  /** Navega al detalle completo de un centro. */
  function goToCenter(id: string): void {
    navigateTo('/donor/center/' + id)
  }

  /**
   * Inicia el flujo de donación a un centro. Navega a `/donor/donate/:id`; si el
   * visitante no tiene sesión de donante, el middleware `auth-donor` de esa ruta
   * lo desvía a `/login?redirect=...` y lo devuelve al flujo tras autenticar
   * (login diferido). Con sesión de donante entra directo.
   */
  function donate(id: string): void {
    navigateTo('/donor/donate/' + id)
  }

  /** Vuelve al origen (`/donor` en el mapa del donante, `/` en el público). */
  function goBack(): void {
    navigateTo(backTo)
  }

  return {
    // estado
    centers,
    selectedCenter,
    isLoading,
    error,
    // derivados
    criticalCenters,
    totalCenters,
    // acciones
    loadCenters,
    selectCenter,
    clearSelection,
    goToCenter,
    donate,
    goBack
  }
}
