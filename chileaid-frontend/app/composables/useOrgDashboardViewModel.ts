import { computed, ref } from 'vue'
import {
  orgDashboardService,
  type ActiveEmergencyOption,
  type CreateCenterInput,
  type GeocodeResult,
  type OrgCenterDTO,
  type NeedDTO
} from '~/services/orgDashboardService'
import {
  orgProfileService,
  type OrgProfileDTO
} from '~/services/orgProfileService'

/**
 * VIEW-MODEL — Puente reactivo entre el panel de la organización receptora y el
 * modelo.
 *
 * Es el ÚNICO punto de la app que habla con `orgDashboardService`. Expone estado
 * reactivo (ref/computed) y las intenciones (`loadDashboard`, navegación); los
 * componentes nunca tocan el servicio, solo consumen lo que aquí se publica vía
 * props desde la página.
 *
 * Las recepciones (CU-07) viven en su propia pantalla `/org/receptions`
 * (`useOrgReceptionsViewModel`); el dashboard solo ofrece un acceso directo.
 *
 * Nota: las métricas de distribución (recibido/distribuido/terreno…) se retiraron
 * del panel porque NO forman parte de `GET /org/center`; vendrán de un futuro
 * endpoint de distribución (hoy `distributionService` es solo un mock que alimenta
 * la pantalla `/org/distribution`).
 */
export function useOrgDashboardViewModel() {
  const center = ref<OrgCenterDTO | null>(null)
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // Perfil de la org: solo se usa para PREFIJAR el formulario de crear centro
  // (nombre/zona); su carga es defensiva (no rompe el panel si falla).
  const orgProfile = ref<OrgProfileDTO | null>(null)

  // Emergencias activas para el selector del formulario del centro (la org
  // vincula su centro a una de ellas). Carga defensiva: no rompe el panel.
  const activeEmergencies = ref<ActiveEmergencyOption[]>([])

  // Formulario del centro: crear (estado "sin centro") o editar (centro existente)
  const showCenterForm = ref<boolean>(false)
  const centerFormMode = ref<'create' | 'edit'>('create')
  const isSavingCenter = ref<boolean>(false)
  const centerFormError = ref<string | null>(null)

  /** `true` cuando la org tiene un centro registrado (el backend devolvió datos). */
  const hasCenter = computed<boolean>(() => center.value !== null)

  /**
   * Valores iniciales del formulario del centro. En modo **editar** precarga los
   * datos del centro actual (incl. horario y coordenadas); en modo **crear** los
   * prefija con datos ya conocidos de la org (`nombre` = "Centro de Acopio {org}",
   * `zona` = región del perfil; `direccion` no está en el perfil → vacía).
   */
  const centerFormDefaults = computed(() => {
    if (centerFormMode.value === 'edit' && center.value) {
      return {
        nombre: center.value.nombre,
        direccion: center.value.direccion,
        zona: center.value.zona,
        horarioAtencion: center.value.horarioAtencion ?? '',
        latitud: center.value.latitud,
        longitud: center.value.longitud,
        // Vínculo actual (puede ser una emergencia cerrada = histórico); el form
        // lo conserva como opción para no desvincular al editar otros campos.
        emergencia: center.value.emergencia
      }
    }
    return {
      nombre: orgProfile.value ? `Centro de Acopio ${orgProfile.value.nombre}` : '',
      direccion: '',
      zona: orgProfile.value?.region ?? '',
      horarioAtencion: '',
      latitud: null,
      longitud: null,
      emergencia: null
    }
  })

  /** Necesidades todavía activas (las publicadas y abiertas a donación). */
  const activeNeeds = computed<NeedDTO[]>(() =>
    (center.value?.necesidades ?? []).filter((n) => n.estado === 'activa')
  )

  /** Cantidad de necesidades activas marcadas con urgencia alta. */
  const urgentNeedsCount = computed<number>(
    () => activeNeeds.value.filter((n) => n.urgencia === 'alta').length
  )

  /** Semáforo de la cobertura general del centro (desde `totales`). */
  const coberturaColor = computed<'critico' | 'warning' | 'ok'>(() => {
    const c = center.value?.totales.coberturaGeneral ?? 0
    if (c < 30) return 'critico'
    if (c < 70) return 'warning'
    return 'ok'
  })

  /**
   * Carga el centro (real) y, en paralelo, el perfil (para prefijar el form de
   * crear). Maneja loading y error de forma centralizada. `getOrgCenter` devuelve
   * `null` si la org no tiene centro: no es un error, lo refleja `hasCenter`.
   */
  async function loadDashboard(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const [centerData, profileData, emergenciesData] = await Promise.all([
        orgDashboardService.getOrgCenter(),
        // Solo para prefijar el form de crear centro: si falla, no rompe el panel.
        orgProfileService.getOrgProfile().catch(() => null),
        // Solo alimenta el selector de emergencia del form: carga defensiva.
        orgDashboardService.getActiveEmergencies().catch(() => [])
      ])
      center.value = centerData
      orgProfile.value = profileData
      activeEmergencies.value = emergenciesData
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'No se pudo cargar el panel.'
    } finally {
      isLoading.value = false
    }
  }

  /** Abre el formulario en modo CREAR (estado "sin centro"); limpia errores. */
  function openCenterForm(): void {
    centerFormMode.value = 'create'
    centerFormError.value = null
    showCenterForm.value = true
  }

  /** Abre el formulario en modo EDITAR (precarga el centro actual); limpia errores. */
  function openEditCenterForm(): void {
    centerFormMode.value = 'edit'
    centerFormError.value = null
    showCenterForm.value = true
  }

  /** Cierra el formulario del centro. */
  function closeCenterForm(): void {
    showCenterForm.value = false
  }

  /**
   * Guarda el formulario del centro: crea (`POST`) o edita (`PUT`) según el modo.
   * En éxito coloca el centro devuelto en el estado (al crear, `hasCenter` pasa a
   * `true` y se muestra el panel) y cierra el formulario; en error expone el
   * mensaje del backend (409/422).
   */
  async function submitCenter(input: CreateCenterInput): Promise<void> {
    if (isSavingCenter.value) return

    isSavingCenter.value = true
    centerFormError.value = null
    try {
      const saved =
        centerFormMode.value === 'edit'
          ? await orgDashboardService.updateCenter(input)
          : await orgDashboardService.createCenter(input)
      center.value = saved
      showCenterForm.value = false
    } catch (e) {
      centerFormError.value =
        e instanceof Error ? e.message : 'No se pudo guardar el centro.'
    } finally {
      isSavingCenter.value = false
    }
  }

  /**
   * Geocodifica una dirección para el selector de mapa del formulario del centro
   * (RF-05). Es el único punto que habla con el service; el `OrgCenterForm` la
   * recibe como prop-función y la invoca al pulsar "Ubicar por dirección" (nunca
   * importa el service). Devuelve el punto sugerido o `null`.
   */
  async function geocodeAddress(query: string): Promise<GeocodeResult | null> {
    return orgDashboardService.geocodeAddress(query)
  }

  /** Navega a la gestión de necesidades del centro. */
  function goToNeeds(): void {
    navigateTo('/org/needs')
  }

  /** Navega a la pantalla de confirmación de recepciones (CU-07). */
  function goToReceptions(): void {
    navigateTo('/org/receptions')
  }

  return {
    // estado
    center,
    isLoading,
    error,
    showCenterForm,
    centerFormMode,
    isSavingCenter,
    centerFormError,
    activeEmergencies,
    // derivados
    hasCenter,
    centerFormDefaults,
    activeNeeds,
    urgentNeedsCount,
    coberturaColor,
    // acciones
    loadDashboard,
    openCenterForm,
    openEditCenterForm,
    closeCenterForm,
    submitCenter,
    geocodeAddress,
    goToNeeds,
    goToReceptions
  }
}
